import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import AppointmentCard from '../components/AppointmentCard';
import AppointmentForm from '../components/AppointmentForm';
import AIAssistant from '../components/AIAssistant';

const Dashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState(null);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/appointments');
      if (response.success) {
        setAppointments(sortAppointments(response.data));
      }
    } catch (err) {
      setError('Erro ao carregar agendamentos.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const sortAppointments = (items) => {
    return items.sort((a, b) => {
      const now = new Date();
      const dateA = new Date(a.service_date);
      const dateB = new Date(b.service_date);
      
      // 1. Delayed appointments first
      const isDelayedA = dateA < now && a.status !== 'completed';
      const isDelayedB = dateB < now && b.status !== 'completed';
      
      if (isDelayedA && !isDelayedB) return -1;
      if (!isDelayedA && isDelayedB) return 1;
      if (isDelayedA && isDelayedB) return dateA - dateB; // Most delayed first? Or oldest first? Oldest first implies most delayed.
      
      // 2. Chronological order for the rest
      return dateA - dateB;
    });
  };

  const handleEdit = (appointment) => {
    setEditingAppointment(appointment);
    setShowForm(true);
  };

  const handleSuccess = () => {
    setShowForm(false);
    setEditingAppointment(null);
    fetchAppointments();
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingAppointment(null);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Painel de Agendamentos</h2>
        <button 
          className="btn btn-primary" 
          onClick={() => {
            setEditingAppointment(null);
            setShowForm(true);
          }}
        >
          + Novo Agendamento
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingAppointment ? 'Editar Agendamento' : 'Novo Agendamento'}</h3>
              <button className="btn-close" onClick={handleCancel}>&times;</button>
            </div>
            <AppointmentForm onSuccess={handleSuccess} initialData={editingAppointment} />
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Carregando...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="appointments-grid">
          {appointments.length === 0 ? (
            <p className="no-data">Nenhum agendamento encontrado.</p>
          ) : (
            appointments.map(app => (
              <AppointmentCard
                key={app.id}
                appointment={app}
                onEdit={handleEdit}
                onUpdate={fetchAppointments}
              />
            ))
          )}
        </div>
      )}
      
      <AIAssistant onActionComplete={fetchAppointments} />
    </div>
  );
};

export default Dashboard;