import React, { useState, useEffect } from 'react'
import AppointmentForm from '../components/AppointmentForm.jsx'
import apiService from '../services/api.js'

function Dashboard() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingAppointment, setEditingAppointment] = useState(null)

  useEffect(() => {
    // Fetch appointments from API
    const fetchAppointments = async () => {
      try {
        const response = await apiService.getAppointments()
        
        if (response.success) {
          setAppointments(response.data)
        }
      } catch (error) {
        console.error('Error fetching appointments:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAppointments()
  }, [])

  const handleCreateAppointment = () => {
    setEditingAppointment(null)
    setShowForm(true)
  }

  const handleEditAppointment = (appointment) => {
    setEditingAppointment(appointment)
    setShowForm(true)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingAppointment(null)
  }

  const handleSaveAppointment = async (appointmentData) => {
    try {
      if (editingAppointment) {
        await apiService.updateAppointment(editingAppointment.id, appointmentData)
      } else {
        await apiService.createAppointment(appointmentData)
      }
      
      // Refresh appointments list
      const response = await apiService.getAppointments()
      if (response.success) {
        setAppointments(response.data)
      }
      
      handleCloseForm()
    } catch (error) {
      console.error('Error saving appointment:', error)
      alert('Erro ao salvar agendamento. Tente novamente.')
    }
  }

  const handleCompleteAppointment = async (appointmentId) => {
    try {
      await apiService.completeAppointment(appointmentId)
      
      // Refresh appointments list
      const response = await apiService.getAppointments()
      if (response.success) {
        setAppointments(response.data)
      }
    } catch (error) {
      console.error('Error completing appointment:', error)
      alert('Erro ao concluir agendamento. Tente novamente.')
    }
  }

  if (loading) {
    return <div className="loading">Carregando agendamentos...</div>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Agendamentos</h2>
        <button className="btn btn-primary" onClick={handleCreateAppointment}>
          Novo Agendamento
        </button>
      </div>
      
      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <AppointmentForm
              onSave={handleSaveAppointment}
              onCancel={handleCloseForm}
              initialData={editingAppointment}
            />
          </div>
        </div>
      )}
      
      <div className="appointments-container">
        {appointments.length === 0 ? (
          <div className="empty-state">
            <p>Nenhum agendamento encontrado</p>
            <p>Clique em "Novo Agendamento" para criar seu primeiro agendamento</p>
          </div>
        ) : (
          <div className="appointments-list">
            {appointments.map(appointment => (
              <div key={appointment.id} className="appointment-card">
                <div className="appointment-header">
                  <h3>{appointment.customer_name}</h3>
                  <span className={`status-badge status-${appointment.status}`}>
                    {appointment.status === 'pending' ? 'Pendente' :
                     appointment.status === 'in_progress' ? 'Em Andamento' : 'Concluído'}
                  </span>
                </div>
                
                <div className="appointment-details">
                  <p><strong>Serviço:</strong> {appointment.service_type}</p>
                  <p><strong>Data:</strong> {new Date(appointment.service_date).toLocaleString('pt-BR')}</p>
                  <p><strong>Volatilidade:</strong> {
                    appointment.volatility_level === 'low' ? 'Baixa' :
                    appointment.volatility_level === 'medium' ? 'Média' : 'Alta'
                  }</p>
                  {appointment.observations && (
                    <p><strong>Observações:</strong> {appointment.observations}</p>
                  )}
                </div>
                
                <div className="appointment-actions">
                  <button className="btn btn-secondary" onClick={() => handleEditAppointment(appointment)}>Editar</button>
                  <button className="btn btn-success" onClick={() => handleCompleteAppointment(appointment.id)}>Concluir</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard