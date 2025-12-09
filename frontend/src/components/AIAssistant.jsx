import React, { useState } from 'react';
import { api } from '../services/api';
import Modal from './Modal';
import AppointmentCard from './AppointmentCard';

const AIAssistant = ({ onActionComplete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);
  const [pendingAction, setPendingAction] = useState(null);

  const toggleOpen = () => setIsOpen(!isOpen);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/ai/chat', { message: userMessage });
      
      if (response.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: response.data.message }]);
        
        if (response.data.action && response.data.requires_confirmation) {
          setPendingAction(response.data.action);
          if (response.data.action.recommendation) {
            setRecommendation(response.data.action.recommendation);
          }
        } else if (response.data.action && !response.data.requires_confirmation) {
           // Auto-execute if implemented, for now just show message
        }
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Erro ao processar mensagem. O serviço de IA pode estar indisponível.' }]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const confirmAction = async () => {
    if (!pendingAction) return;
    
    setLoading(true);
    try {
      if (pendingAction.type === 'reschedule') {
        await api.put(`/appointments/${pendingAction.appointment_id}`, {
          service_date: pendingAction.new_date
        });
        setMessages(prev => [...prev, { role: 'assistant', content: 'Agendamento reagendado com sucesso!' }]);
      }
      // Handle other action types like 'recommend' (creating new from recommendation) if needed
      
      setPendingAction(null);
      setRecommendation(null);
      if (onActionComplete) onActionComplete();
      
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Erro ao executar ação.' }]);
    } finally {
      setLoading(false);
    }
  };

  const cancelAction = () => {
    setPendingAction(null);
    setRecommendation(null);
    setMessages(prev => [...prev, { role: 'assistant', content: 'Ação cancelada.' }]);
  };

  return (
    <div className={`ai-assistant ${isOpen ? 'open' : ''}`}>
      <div className="ai-toggle" onClick={toggleOpen}>
        {isOpen ? '✕' : '🤖'}
      </div>

      {isOpen && (
        <div className="ai-window">
          <div className="ai-header">
            <h3>Assistente Maxfrio</h3>
          </div>
          
          <div className="ai-messages">
            {messages.length === 0 && (
              <p className="ai-welcome">Olá! Como posso ajudar com os agendamentos hoje?</p>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {loading && <div className="message loading">Pensando...</div>}
            
            {pendingAction && (
              <div className="ai-action-confirm">
                <p>Confirma esta ação?</p>
                {recommendation && (
                   <div className="recommendation-preview">
                     <strong>Recomendação:</strong>
                     <AppointmentCard appointment={recommendation} onEdit={() => {}} />
                   </div>
                )}
                <div className="ai-buttons">
                  <button className="btn btn-primary" onClick={confirmAction}>Confirmar</button>
                  <button className="btn btn-secondary" onClick={cancelAction}>Cancelar</button>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSend} className="ai-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua mensagem..."
              disabled={loading || !!pendingAction}
            />
            <button type="submit" disabled={loading || !!pendingAction || !input.trim()}>➤</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;