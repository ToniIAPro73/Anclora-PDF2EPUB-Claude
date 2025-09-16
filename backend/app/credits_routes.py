"""
Rutas API para gestión de créditos en Anclora PDF2EPUB
"""

from flask import Blueprint, request, jsonify
import logging
from .supabase_auth import supabase_auth_required, get_current_user_id
from .credits_service import credits_service
from . import limiter

bp = Blueprint('credits', __name__)
logger = logging.getLogger(__name__)

@bp.route('/api/credits/balance', methods=['GET'])
@supabase_auth_required
def get_credit_balance():
    """Obtiene el balance actual de créditos del usuario"""
    try:
        user_id = get_current_user_id()
        balance = credits_service.get_user_credits(user_id)

        return jsonify({
            'success': True,
            'balance': balance
        }), 200

    except Exception as e:
        logger.error(f"Error getting credit balance: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get credit balance'
        }), 500

@bp.route('/api/credits/history', methods=['GET'])
@supabase_auth_required
def get_credit_history():
    """Obtiene el historial de transacciones de créditos"""
    try:
        user_id = get_current_user_id()
        limit = request.args.get('limit', 50, type=int)

        # Validar límite
        if limit > 200:
            limit = 200

        history = credits_service.get_credit_history(user_id, limit)

        return jsonify({
            'success': True,
            'history': history
        }), 200

    except Exception as e:
        logger.error(f"Error getting credit history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get credit history'
        }), 500

@bp.route('/api/credits/cost-estimate', methods=['POST'])
@supabase_auth_required
def estimate_conversion_cost():
    """Estima el costo de una conversión"""
    try:
        data = request.get_json()

        if not data or 'pipeline_id' not in data:
            return jsonify({
                'success': False,
                'error': 'pipeline_id is required'
            }), 400

        pipeline_id = data['pipeline_id']
        page_count = data.get('page_count', 1)

        if page_count < 1:
            page_count = 1

        user_id = get_current_user_id()

        # Calcular costo
        cost = credits_service.calculate_conversion_cost(pipeline_id, page_count)

        # Verificar si puede costear
        can_afford, current_credits, _ = credits_service.can_afford_conversion(user_id, pipeline_id, page_count)

        return jsonify({
            'success': True,
            'cost': cost,
            'can_afford': can_afford,
            'current_credits': current_credits,
            'pipeline_id': pipeline_id,
            'page_count': page_count
        }), 200

    except Exception as e:
        logger.error(f"Error estimating conversion cost: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to estimate cost'
        }), 500

@bp.route('/api/credits/pipeline-costs', methods=['GET'])
@supabase_auth_required
def get_pipeline_costs():
    """Obtiene los costos de todos los pipelines disponibles"""
    try:
        costs = credits_service.get_pipeline_costs()

        # Enriquecer con información adicional
        enriched_costs = []
        for cost_info in costs:
            # Calcular costo para diferentes cantidades de páginas
            pipeline_id = cost_info['pipeline_id']
            base_cost = cost_info['base_cost']
            cost_per_page = cost_info['cost_per_page']

            # Ejemplos de costos
            cost_examples = {
                '1_page': base_cost,
                '10_pages': base_cost + (cost_per_page * 9),
                '50_pages': base_cost + (cost_per_page * 49)
            }

            enriched_costs.append({
                **cost_info,
                'cost_examples': cost_examples
            })

        return jsonify({
            'success': True,
            'pipeline_costs': enriched_costs
        }), 200

    except Exception as e:
        logger.error(f"Error getting pipeline costs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get pipeline costs'
        }), 500

@bp.route('/api/credits/referral/create', methods=['POST'])
@limiter.limit("10 per hour")  # Límite de invitaciones por hora
@supabase_auth_required
def create_referral():
    """Crea una invitación de referido"""
    try:
        data = request.get_json()

        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'email is required'
            }), 400

        email = data['email'].strip().lower()
        phone = data.get('phone', '').strip() if data.get('phone') else None

        # Validación básica de email
        if '@' not in email or len(email) < 5:
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400

        user_id = get_current_user_id()

        # Crear referido
        result = credits_service.create_referral(user_id, email, phone)

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error creating referral: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create referral'
        }), 500

@bp.route('/api/credits/referral/my-code', methods=['GET'])
@supabase_auth_required
def get_my_referral_code():
    """Obtiene el código de referido del usuario"""
    try:
        user_id = get_current_user_id()
        balance = credits_service.get_user_credits(user_id)

        referral_code = balance.get('referral_code')

        if not referral_code:
            return jsonify({
                'success': False,
                'error': 'Referral code not found'
            }), 404

        return jsonify({
            'success': True,
            'referral_code': referral_code,
            'invite_link': f"https://anclora.com/register?ref={referral_code}",
            'remaining_invites': 5  # TODO: Calcular invitaciones restantes
        }), 200

    except Exception as e:
        logger.error(f"Error getting referral code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get referral code'
        }), 500

@bp.route('/api/credits/insufficient', methods=['GET'])
@supabase_auth_required
def insufficient_credits_info():
    """Proporciona información cuando el usuario no tiene suficientes créditos"""
    try:
        user_id = get_current_user_id()
        balance = credits_service.get_user_credits(user_id)

        # Sugerencias para obtener más créditos
        suggestions = [
            {
                'type': 'referral',
                'title': 'Invita a tus amigos',
                'description': f'Gana {credits_service.REFERRAL_BONUS_REFERRER} créditos por cada amigo que se registre',
                'action': 'invite_friends',
                'potential_credits': credits_service.REFERRAL_BONUS_REFERRER
            },
            {
                'type': 'purchase',
                'title': 'Comprar créditos',
                'description': 'Obtén más créditos para continuar convirtiendo documentos',
                'action': 'buy_credits',
                'potential_credits': 100  # Paquete básico
            }
        ]

        return jsonify({
            'success': True,
            'current_balance': balance,
            'suggestions': suggestions,
            'referral_code': balance.get('referral_code')
        }), 200

    except Exception as e:
        logger.error(f"Error getting insufficient credits info: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get credit information'
        }), 500

# Endpoint interno para procesar cargos de conversión
@bp.route('/api/credits/charge-conversion', methods=['POST'])
@supabase_auth_required
def charge_conversion():
    """Cobra créditos por una conversión (uso interno)"""
    try:
        data = request.get_json()

        required_fields = ['conversion_id', 'pipeline_id']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        user_id = get_current_user_id()
        conversion_id = data['conversion_id']
        pipeline_id = data['pipeline_id']
        page_count = data.get('page_count', 1)
        description = data.get('description')

        # Procesar cargo
        result = credits_service.charge_conversion(
            user_id, conversion_id, pipeline_id, page_count, description
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error charging conversion: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to charge conversion'
        }), 500

# Endpoint para obtener estadísticas del usuario
@bp.route('/api/credits/stats', methods=['GET'])
@supabase_auth_required
def get_credit_stats():
    """Obtiene estadísticas de uso de créditos del usuario"""
    try:
        user_id = get_current_user_id()
        balance = credits_service.get_user_credits(user_id)
        history = credits_service.get_credit_history(user_id, 100)  # Últimas 100 transacciones

        # Analizar patrones de uso
        total_conversions = len([t for t in history if t['transaction_type'] == 'conversion_cost'])
        total_referrals = len([t for t in history if t['transaction_type'] == 'referral_bonus'])

        # Pipeline más usado
        pipeline_usage = {}
        for transaction in history:
            if transaction.get('pipeline_id'):
                pipeline_id = transaction['pipeline_id']
                pipeline_usage[pipeline_id] = pipeline_usage.get(pipeline_id, 0) + 1

        most_used_pipeline = max(pipeline_usage.items(), key=lambda x: x[1])[0] if pipeline_usage else None

        stats = {
            'balance': balance,
            'usage_stats': {
                'total_conversions': total_conversions,
                'total_referrals_made': total_referrals,
                'most_used_pipeline': most_used_pipeline,
                'pipeline_usage': pipeline_usage
            },
            'recent_activity': history[:10]  # Últimas 10 transacciones
        }

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting credit stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get credit statistics'
        }), 500