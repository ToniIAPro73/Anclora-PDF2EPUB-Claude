"""
Servicio de gestión de créditos para Anclora PDF2EPUB
Maneja todas las operaciones relacionadas con créditos de usuario
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from supabase import Client
from .supabase_client import get_supabase_client
from .models import CreditTransaction, PipelineCost
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class CreditsService:
    """Servicio para gestión de créditos de usuario"""

    def __init__(self):
        self.supabase: Client = get_supabase_client()

        # Configuración de créditos por defecto
        self.DEFAULT_INITIAL_CREDITS = 100
        self.REFERRAL_BONUS_REFERRER = 25  # Créditos para quien refiere
        self.REFERRAL_BONUS_REFERRED = 50  # Créditos para quien es referido

        # Costos por defecto si no están en BD
        self.DEFAULT_PIPELINE_COSTS = {
            'engines.low': {'base_cost': 1, 'cost_per_page': 0},
            'engines.medium': {'base_cost': 3, 'cost_per_page': 1},
            'engines.high': {'base_cost': 8, 'cost_per_page': 2},
        }

    def get_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Obtiene el balance actual de créditos del usuario"""
        try:
            # Obtener datos del perfil
            profile_result = self.supabase.table('profiles').select(
                'credits, total_earned_credits, referral_code'
            ).eq('user_id', user_id).single().execute()

            if not profile_result.data:
                logger.warning(f"Profile not found for user {user_id}")
                return {
                    'current_credits': 0,
                    'total_earned': 0,
                    'total_spent': 0,
                    'referral_code': None
                }

            profile = profile_result.data

            # Obtener historial de transacciones para calcular total gastado
            transactions_result = self.supabase.table('credit_transactions').select(
                'amount, transaction_type'
            ).eq('user_id', user_id).execute()

            total_spent = 0
            if transactions_result.data:
                for transaction in transactions_result.data:
                    if transaction['amount'] < 0:
                        total_spent += abs(transaction['amount'])

            return {
                'current_credits': profile.get('credits', 0),
                'total_earned': profile.get('total_earned_credits', 0),
                'total_spent': total_spent,
                'referral_code': profile.get('referral_code')
            }

        except Exception as e:
            logger.error(f"Error getting user credits for {user_id}: {e}")
            return {
                'current_credits': 0,
                'total_earned': 0,
                'total_spent': 0,
                'referral_code': None
            }

    def calculate_conversion_cost(self, pipeline_id: str, page_count: int = 1) -> int:
        """Calcula el costo de una conversión"""
        try:
            # Intentar obtener costo de la BD
            cost_result = self.supabase.table('pipeline_costs').select(
                'base_cost, cost_per_page'
            ).eq('pipeline_id', pipeline_id).eq('active', True).single().execute()

            if cost_result.data:
                base_cost = cost_result.data['base_cost']
                cost_per_page = cost_result.data['cost_per_page']
            else:
                # Usar costos por defecto
                if pipeline_id in self.DEFAULT_PIPELINE_COSTS:
                    costs = self.DEFAULT_PIPELINE_COSTS[pipeline_id]
                    base_cost = costs['base_cost']
                    cost_per_page = costs['cost_per_page']
                else:
                    # Pipeline desconocido, usar costo medio
                    base_cost = 5
                    cost_per_page = 1

            # Calcular costo total
            total_cost = base_cost + (cost_per_page * max(page_count - 1, 0))

            logger.info(f"Cost calculation for {pipeline_id}: base={base_cost}, per_page={cost_per_page}, pages={page_count}, total={total_cost}")

            return total_cost

        except Exception as e:
            logger.error(f"Error calculating cost for {pipeline_id}: {e}")
            # En caso de error, retornar costo por defecto
            return 5

    def can_afford_conversion(self, user_id: str, pipeline_id: str, page_count: int = 1) -> Tuple[bool, int, int]:
        """
        Verifica si el usuario puede costear una conversión
        Retorna: (puede_costear, créditos_actuales, costo_conversión)
        """
        user_credits = self.get_user_credits(user_id)
        current_credits = user_credits['current_credits']
        conversion_cost = self.calculate_conversion_cost(pipeline_id, page_count)

        can_afford = current_credits >= conversion_cost

        return can_afford, current_credits, conversion_cost

    def charge_conversion(self, user_id: str, conversion_id: str, pipeline_id: str,
                         page_count: int = 1, description: Optional[str] = None) -> Dict[str, Any]:
        """Cobra los créditos por una conversión"""
        try:
            # Verificar si puede costear
            can_afford, current_credits, cost = self.can_afford_conversion(user_id, pipeline_id, page_count)

            if not can_afford:
                return {
                    'success': False,
                    'error': 'Insufficient credits',
                    'current_credits': current_credits,
                    'required_credits': cost
                }

            # Procesar transacción usando función de BD
            result = self.supabase.rpc('process_credit_transaction', {
                'p_user_id': user_id,
                'p_amount': -cost,  # Negativo porque es un gasto
                'p_transaction_type': 'conversion_cost',
                'p_conversion_id': conversion_id,
                'p_pipeline_id': pipeline_id,
                'p_description': description or f'Conversión usando {pipeline_id}',
                'p_metadata': {
                    'page_count': page_count,
                    'cost_breakdown': {
                        'base_cost': self.DEFAULT_PIPELINE_COSTS.get(pipeline_id, {}).get('base_cost', 5),
                        'cost_per_page': self.DEFAULT_PIPELINE_COSTS.get(pipeline_id, {}).get('cost_per_page', 0),
                        'total_pages': page_count
                    }
                }
            }).execute()

            if result.data:
                return {
                    'success': True,
                    'credits_charged': cost,
                    'remaining_credits': current_credits - cost,
                    'transaction_id': f"conv_{conversion_id}"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to process transaction'
                }

        except Exception as e:
            logger.error(f"Error charging conversion for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Transaction error: {str(e)}'
            }

    def grant_initial_credits(self, user_id: str) -> Dict[str, Any]:
        """Otorga créditos iniciales a un nuevo usuario"""
        try:
            result = self.supabase.rpc('process_credit_transaction', {
                'p_user_id': user_id,
                'p_amount': self.DEFAULT_INITIAL_CREDITS,
                'p_transaction_type': 'initial_bonus',
                'p_description': f'Créditos de bienvenida (+{self.DEFAULT_INITIAL_CREDITS})',
                'p_metadata': {'bonus_type': 'welcome_bonus'}
            }).execute()

            if result.data:
                return {
                    'success': True,
                    'credits_granted': self.DEFAULT_INITIAL_CREDITS,
                    'message': f'¡Bienvenido! Has recibido {self.DEFAULT_INITIAL_CREDITS} créditos gratuitos'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to grant initial credits'
                }

        except Exception as e:
            logger.error(f"Error granting initial credits for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to grant credits: {str(e)}'
            }

    def get_pipeline_costs(self) -> List[Dict[str, Any]]:
        """Obtiene todos los costos de pipelines activos"""
        try:
            result = self.supabase.table('pipeline_costs').select(
                'pipeline_id, base_cost, cost_per_page, description'
            ).eq('active', True).execute()

            if result.data:
                return result.data
            else:
                # Retornar costos por defecto
                return [
                    {
                        'pipeline_id': 'engines.low',
                        'base_cost': 1,
                        'cost_per_page': 0,
                        'description': 'Pipeline rápido - Calidad básica'
                    },
                    {
                        'pipeline_id': 'engines.medium',
                        'base_cost': 3,
                        'cost_per_page': 1,
                        'description': 'Pipeline equilibrado - Calidad media'
                    },
                    {
                        'pipeline_id': 'engines.high',
                        'base_cost': 8,
                        'cost_per_page': 2,
                        'description': 'Pipeline de calidad - Máxima calidad'
                    }
                ]

        except Exception as e:
            logger.error(f"Error getting pipeline costs: {e}")
            return []

    def get_credit_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene el historial de transacciones de créditos del usuario"""
        try:
            result = self.supabase.table('credit_transactions').select(
                'amount, transaction_type, description, created_at, conversion_id, pipeline_id'
            ).eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Error getting credit history for user {user_id}: {e}")
            return []

    def create_referral(self, referrer_id: str, email: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Crea una invitación de referido"""
        try:
            # Obtener código de referido del usuario
            profile_result = self.supabase.table('profiles').select(
                'referral_code'
            ).eq('user_id', referrer_id).single().execute()

            if not profile_result.data or not profile_result.data.get('referral_code'):
                return {
                    'success': False,
                    'error': 'Referral code not found for user'
                }

            referral_code = profile_result.data['referral_code']

            # Crear registro de referido
            referral_data = {
                'referrer_id': referrer_id,
                'referral_code': referral_code,
                'email_invited': email,
                'phone_invited': phone,
                'status': 'pending'
            }

            result = self.supabase.table('referrals').insert(referral_data).execute()

            if result.data:
                return {
                    'success': True,
                    'referral_code': referral_code,
                    'invitation_id': result.data[0]['id'],
                    'invite_link': f"https://anclora.com/register?ref={referral_code}"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create referral'
                }

        except Exception as e:
            logger.error(f"Error creating referral for user {referrer_id}: {e}")
            return {
                'success': False,
                'error': f'Referral creation failed: {str(e)}'
            }


# Instancia global del servicio
credits_service = CreditsService()