import React, { useState } from 'react'
import apiService from '../services/api.js'

function AppointmentForm({ onSave, onCancel, initialData = null }) {
  const [formData, setFormData] = useState({
    customer_name: initialData?.customer_name || '',
    service_date: initialData?.service_date || '',
    service_type: initialData?.service_type || '',
    volatility_level: initialData?.volatility_level || 'medium',
    observations: initialData?.observations || '',
    required_tools: initialData?.required_tools || []
  })

  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleToolChange = (index, value) => {
    const newTools = [...formData.required_tools]
    newTools[index] = value
    setFormData(prev => ({
      ...prev,
      required_tools: newTools
    }))
  }

  const addTool = () => {
    setFormData(prev => ({
      ...prev,
      required_tools: [...prev.required_tools, '']
    }))
  }

  const removeTool = (index) => {
    const newTools = formData.required_tools.filter((_, i) => i !== index)
    setFormData(prev => ({
      ...prev,
      required_tools: newTools
    }))
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.customer_name || formData.customer_name.length < 2) {
      newErrors.customer_name = 'Nome do cliente é obrigatório (mínimo 2 caracteres)'
    }
    
    if (!formData.service_date) {
      newErrors.service_date = 'Data do serviço é obrigatória'
    } else {
      const selectedDate = new Date(formData.service_date)
      const now = new Date()
      if (selectedDate <= now) {
        newErrors.service_date = 'Data do serviço deve ser no futuro'
      }
    }
    
    if (!formData.service_type || formData.service_type.length < 2) {
      newErrors.service_type = 'Tipo de serviço é obrigatório (mínimo 2 caracteres)'
    }
    
    if (formData.observations && formData.observations.length > 500) {
      newErrors.observations = 'Observações devem ter no máximo 500 caracteres'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const appointmentData = {
        ...formData,
        service_date: new Date(formData.service_date).toISOString()
      }
      
      if (initialData?.id) {
        // Update existing appointment
        await apiService.updateAppointment(initialData.id, appointmentData)
      } else {
        // Create new appointment
        await apiService.createAppointment(appointmentData)
      }
      
      onSave()
    } catch (error) {
      console.error('Error saving appointment:', error)
      alert('Erro ao salvar agendamento. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const volatilityOptions = [
    { value: 'low', label: 'Baixa' },
    { value: 'medium', label: 'Média' },
    { value: 'high', label: 'Alta' }
  ]

  return (
    <div className="appointment-form">
      <h2>{initialData?.id ? 'Editar Agendamento' : 'Novo Agendamento'}</h2>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="customer_name">Nome do Cliente *</label>
          <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleInputChange}
            className={errors.customer_name ? 'error' : ''}
            placeholder="Digite o nome do cliente"
            disabled={isSubmitting}
          />
          {errors.customer_name && <span className="error-message">{errors.customer_name}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="service_date">Data e Hora do Serviço *</label>
          <input
            type="datetime-local"
            id="service_date"
            name="service_date"
            value={formData.service_date}
            onChange={handleInputChange}
            className={errors.service_date ? 'error' : ''}
            disabled={isSubmitting}
          />
          {errors.service_date && <span className="error-message">{errors.service_date}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="service_type">Tipo de Serviço *</label>
          <input
            type="text"
            id="service_type"
            name="service_type"
            value={formData.service_type}
            onChange={handleInputChange}
            className={errors.service_type ? 'error' : ''}
            placeholder="Ex: Manutenção de Ar Condicionado"
            disabled={isSubmitting}
          />
          {errors.service_type && <span className="error-message">{errors.service_type}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="volatility_level">Volatilidade do Cliente *</label>
          <select
            id="volatility_level"
            name="volatility_level"
            value={formData.volatility_level}
            onChange={handleInputChange}
            disabled={isSubmitting}
          >
            {volatilityOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="observations">Observações</label>
          <textarea
            id="observations"
            name="observations"
            value={formData.observations}
            onChange={handleInputChange}
            className={errors.observations ? 'error' : ''}
            placeholder="Informações adicionais sobre o serviço"
            rows="3"
            disabled={isSubmitting}
          />
          {errors.observations && <span className="error-message">{errors.observations}</span>}
        </div>

        <div className="form-group">
          <label>Ferramentas Necessárias</label>
          <div className="tools-container">
            {formData.required_tools.map((tool, index) => (
              <div key={index} className="tool-input">
                <input
                  type="text"
                  value={tool}
                  onChange={(e) => handleToolChange(index, e.target.value)}
                  placeholder="Nome da ferramenta"
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={() => removeTool(index)}
                  className="btn btn-danger btn-small"
                  disabled={isSubmitting}
                >
                  Remover
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={addTool}
              className="btn btn-secondary btn-small"
              disabled={isSubmitting}
            >
              Adicionar Ferramenta
            </button>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Salvando...' : (initialData?.id ? 'Atualizar' : 'Salvar')}
          </button>
        </div>
      </form>
    </div>
  )
}

export default AppointmentForm