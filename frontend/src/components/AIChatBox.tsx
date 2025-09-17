import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

interface AIChatBoxProps {
  userCredits: number;
  selectedPipeline: string;
  pipelines: any[];
  analysisData?: any;
  onSequenceRecommended?: (sequence: any) => void;
}

interface ChatMessage {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
}

const AIChatBox: React.FC<AIChatBoxProps> = ({
  userCredits,
  selectedPipeline,
  pipelines,
  analysisData,
  onSequenceRecommended
}) => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasUnreadMessages, setHasUnreadMessages] = useState(false);
  const [hasOptimalSequence, setHasOptimalSequence] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Función para generar recomendaciones de IA
  const generateAIResponse = () => {
    let response = "";

    // Verificar créditos
    if (userCredits < 10) {
      response += `⚠️ Tu balance actual es de ${userCredits} créditos. `;

      if (userCredits === 0) {
        response += "Necesitas al menos 1 crédito para realizar conversiones.";
        return response;
      } else if (userCredits < 6) {
        response += "Solo puedes usar la conversión Rápida (1 crédito).";
      } else if (userCredits < 10) {
        response += "Puedes usar conversión Rápida (1 crédito) o Intermedia (6 créditos).";
      }
      response += "\n\n";
    }

    // Análisis del documento
    if (analysisData) {
      response += `📄 He analizado tu documento:\n`;
      response += `• ${analysisData.page_count} páginas\n`;
      response += `• Tipo: ${analysisData.content_type}\n`;
      response += `• Complejidad: ${analysisData.complexity_score}/5\n\n`;

      // Recomendación basada en complejidad
      if (analysisData.issues?.length > 0) {
        response += `🔍 Detecté: ${analysisData.issues.join(', ')}\n\n`;

        // Sugerir secuencia especial si es necesario
        if (analysisData.issues.some((issue: string) =>
          issue.includes('Tables') || issue.includes('Formulas')
        )) {
          const sequenceCost = 15; // Costo de secuencia especial
          if (userCredits >= sequenceCost) {
            setHasOptimalSequence(true); // Activar notificación de secuencia óptima
            response += `💡 Recomiendo una secuencia especial de conversión:\n`;
            response += `📋 Secuencia: PDF2HTMLEx → Pandoc MathML → Optimización\n`;
            response += `💰 Costo: ${sequenceCost} créditos\n`;
            response += `⭐ Calidad estimada: 98%\n\n`;
            response += `¿Prefieres usar esta secuencia o una de las opciones estándar?`;
            return response;
          }
        }
      }

      // Recomendación estándar
      const recommendedOption = pipelines.find(p => p.id === analysisData.recommended);
      if (recommendedOption && userCredits >= recommendedOption.estimated_cost) {
        response += `✨ Te recomiendo usar "${t(`engines.${recommendedOption.quality}`)}" `;
        response += `(${recommendedOption.estimated_cost} créditos) para este documento.\n\n`;
      }
    }

    response += `💳 Tienes ${userCredits} créditos disponibles.`;

    return response;
  };

  // Generar mensaje inicial cuando se carga
  useEffect(() => {
    if (pipelines.length > 0 && userCredits !== undefined) {
      const initialMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: generateAIResponse(),
        timestamp: new Date()
      };
      setMessages([initialMessage]);
      setHasUnreadMessages(true); // Marcar como no leído cuando llega un nuevo mensaje
    }
  }, [pipelines, userCredits, analysisData]);

  // Determinar qué tipo de notificación mostrar
  const getNotificationIcon = () => {
    // Prioridad 1: Alerta de créditos bajos (no desaparece hasta que tenga >10 créditos)
    if (userCredits <= 10) {
      return { icon: '⚠️', color: 'bg-red-500', animate: true };
    }

    // Prioridad 2: Secuencia óptima disponible (campanita)
    if (hasOptimalSequence) {
      return { icon: '🔔', color: 'bg-blue-500', animate: true };
    }

    // Prioridad 3: Mensajes sin leer normales (campanita)
    if (hasUnreadMessages) {
      return { icon: '🔔', color: 'bg-yellow-400', animate: true };
    }

    return null;
  };

  // Manejar apertura del chat - marcar mensajes como leídos
  const handleChatOpen = () => {
    setIsExpanded(true);
    setHasUnreadMessages(false); // Marcar mensajes normales como leídos
    setHasOptimalSequence(false); // Marcar secuencia óptima como vista
  };

  const addMessage = (content: string, type: 'ai' | 'user') => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    if (type === 'ai' && !isExpanded) {
      setHasUnreadMessages(true); // Marcar como no leído si llega mensaje IA y el chat está cerrado
    }
  };

  return (
    <div className="transition-all duration-300">
      {isExpanded ? (
        /* Chat expandido - ajustado al ancho de la columna */
        <div className="w-full h-96 max-w-sm" style={{ marginTop: '-50px' }}>
          <div className="bg-white rounded-lg shadow-xl border-2 border-blue-200 h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-3 text-white rounded-t-lg" style={{ background: 'var(--gradient-nexus)' }}>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="font-semibold text-sm">Asistente IA</span>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-xs opacity-80 hover:opacity-100 transition-opacity"
              >
                ✕
              </button>
            </div>

            {/* Mensajes */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs p-3 rounded-lg text-sm ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-800 rounded-bl-none'
                    }`}
                  >
                    <div className="whitespace-pre-line">{message.content}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="p-3 border-t bg-gray-50 rounded-b-lg">
              <div className="text-xs text-gray-500 text-center">
                Asistente automático • Análisis de documentos
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Icono cerrado */
        <div className="flex justify-center">
          <button
            onClick={handleChatOpen}
            className="w-16 h-16 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center relative"
            style={{ background: 'var(--gradient-nexus)' }}
          >
            <span className="text-2xl">🤖</span>
            {/* Sistema de notificaciones inteligente */}
            {(() => {
              const notification = getNotificationIcon();
              return notification ? (
                <div className={`absolute -top-1 -right-1 w-6 h-6 ${notification.color} rounded-full flex items-center justify-center ${notification.animate ? 'animate-pulse' : ''}`}>
                  <span className="text-sm">{notification.icon}</span>
                </div>
              ) : null;
            })()}
          </button>
        </div>
      )}
    </div>
  );
};

export default AIChatBox;