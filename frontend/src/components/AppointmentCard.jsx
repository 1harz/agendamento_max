import React, { useState } from 'react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { api } from '../services/api';
import Modal from './Modal';

const AppointmentCard = ({ appointment, onEdit, onUpdate }) => {
  const [showHistory, setShowHistory] = useState(false);

  const handleComplete = async () => {
    if (window.confirm("Tem certeza que deseja marcar este serviço como concluído?")) {
      try {
        await api.post(`/appointments/${appointment.id}/complete`);
        if (onUpdate) onUpdate();
      } catch (err) {
        alert("Erro ao concluir agendamento.");
        console.error(err);
      }
    }
  };

  const handlePaid = async () => {
    if (window.confirm("Tem certeza que deseja marcar este serviço como pago?")) {
      try {
        await api.post(`/appointments/${appointment.id}/paid`);
        if (onUpdate) onUpdate();
      } catch (err) {
        alert("Erro ao marcar serviço como pago.");
        console.error(err);
      }
    }
  };

  const getStatusColor = (status, serviceDate) => {
    if (status === 'finalized') return 'status-completed';
    if (status === 'awaiting_payment') return 'status-awaiting-payment';
    if (status === 'completed') return 'status-completed';
    if (status === 'in_progress') return 'status-in-progress';
    
    // Check if delayed
    if (new Date(serviceDate) < new Date() && status !== 'completed' && status !== 'finalized') {
      return 'status-delayed';
    }
    
    return 'status-pending';
  };

  const statusClass = getStatusColor(appointment.status, appointment.service_date);
  
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), "dd 'de' MMMM 'às' HH:mm", { locale: ptBR });
    } catch (e) {
      return dateString;
    }
  };

  const translateStatus = (status) => {
    const map = {
      'pending': 'Pendente',
      'in_progress': 'Em Andamento',
      'completed': 'Concluído',
      'awaiting_payment': 'Aguardando Pagamento',
      'finalized': 'Finalizado'
    };
    return map[status] || status;
  };

  const translateVolatility = (level) => {
    const map = {
      'low': 'Baixa',
      'medium': 'Média',
      'high': 'Alta'
    };
    return map[level] || level;
  };

  return (
    <div className={`appointment-card ${statusClass}`}>
      <div className="card-header">
        <h3 className="customer-name">{appointment.customer_name}</h3>
        <span className="appointment-date">{formatDate(appointment.service_date)}</span>
      </div>
      
      <div className="card-body">
        <div className="info-row">
          <strong>Serviço:</strong> <span data-full-text={appointment.service_type}>{appointment.service_type}</span>
        </div>
        
        <div className="info-row">
          <strong>Status:</strong> <span className={`badge ${statusClass}`}>{translateStatus(appointment.status)}</span>
        </div>
        
        <div className="info-row">
          <strong>Flexibilidade:</strong> <span data-full-text={translateVolatility(appointment.volatility_level)}>{translateVolatility(appointment.volatility_level)}</span>
        </div>
        
        {appointment.required_tools && appointment.required_tools.length > 0 && (
          <div className="info-row">
            <strong>Ferramentas:</strong> <span data-full-text={appointment.required_tools.join(', ')}>{appointment.required_tools.join(', ')}</span>
          </div>
        )}
        
        {appointment.observations && (
          <div className="info-row observations">
            <strong>Obs:</strong> <span data-full-text={appointment.observations}>{appointment.observations}</span>
          </div>
        )}
      </div>
      
      <div className="card-footer">
        {appointment.status === 'awaiting_payment' && (
          <button className="btn btn-primary" onClick={handlePaid}>
            Pago
          </button>
        )}
        {appointment.status !== 'completed' && appointment.status !== 'awaiting_payment' && appointment.status !== 'finalized' && (
          <button className="btn btn-success" onClick={handleComplete}>
            Concluir
          </button>
        )}
        <button className="btn btn-info" onClick={() => setShowHistory(true)}>
          Histórico
        </button>
        <button className="btn btn-secondary" onClick={() => onEdit(appointment)}>
          Editar
        </button>
      </div>

      {showHistory && (
        <Modal title="Histórico de Ocorrências" onClose={() => setShowHistory(false)}>
          {appointment.occurrences && appointment.occurrences.length > 0 ? (
            <ul className="occurrence-list">
              {appointment.occurrences.map(occ => (
                <li key={occ.id}>
                  <strong>{format(new Date(occ.timestamp), "dd/MM/yyyy HH:mm")}</strong>: {occ.description}
                </li>
              ))}
            </ul>
          ) : (
            <p>Nenhuma ocorrência registrada.</p>
          )}
        </Modal>
      )}
    </div>
  );
};

export default AppointmentCard;