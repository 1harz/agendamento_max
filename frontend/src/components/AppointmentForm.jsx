import React, { useState } from 'react';
import { api } from '../services/api';

import { useEffect } from 'react';

const AppointmentForm = ({ onSuccess, initialData }) => {
  const [formData, setFormData] = useState({
    customer_name: '',
    service_date: '',
    service_type: '',
    volatility_level: 'medium',
    observations: '',
    required_tools: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        customer_name: initialData.customer_name,
        service_date: initialData.service_date ? initialData.service_date.slice(0, 16) : '',
        service_type: initialData.service_type,
        volatility_level: initialData.volatility_level,
        observations: initialData.observations || '',
        required_tools: initialData.required_tools ? initialData.required_tools.join(', ') : ''
      });
    }
  }, [initialData]);

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const validateForm = () => {
    if (!formData.customer_name || formData.customer_name.length < 2) {
      setError('Nome do cliente deve ter pelo menos 2 caracteres');
      return false;
    }
    if (!formData.service_date) {
      setError('Data do serviço é obrigatória');
      return false;
    }
    const date = new Date(formData.service_date);
    if (date <= new Date()) {
      setError('Data do serviço deve ser no futuro');
      return false;
    }
    if (!formData.service_type || formData.service_type.length < 2) {
      setError('Tipo de serviço é obrigatório');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      // Process required_tools string into array
      const toolsArray = formData.required_tools
        ? formData.required_tools.split(',').map(tool => tool.trim()).filter(tool => tool)
        : [];

      const payload = {
        ...formData,
        required_tools: toolsArray
      };

      let response;
      if (initialData && initialData.id) {
        response = await api.put(`/appointments/${initialData.id}`, payload);
      } else {
        response = await api.post('/appointments', payload);
      }
      
      if (response.success) {
        setSuccessMessage(initialData ? 'Agendamento atualizado com sucesso!' : 'Agendamento criado com sucesso!');
        if (!initialData) {
          setFormData({
            customer_name: '',
            service_date: '',
            service_type: '',
            volatility_level: 'medium',
            observations: '',
            required_tools: ''
          });
        }
        if (onSuccess) onSuccess();
      }
    } catch (err) {
      console.error('Error saving appointment:', err);
      setError(err.message || 'Erro ao salvar agendamento. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="appointment-form-container">
      {/* <h2>{initialData ? 'Editar Agendamento' : 'Novo Agendamento'}</h2> - Header is now handled by modal */}
      
      {error && <div className="alert alert-danger">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="customer_name">Nome do Cliente *</label>
          <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleChange}
            placeholder="Ex: João Silva"
            required
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="service_date">Data e Hora *</label>
          <input
            type="datetime-local"
            id="service_date"
            name="service_date"
            value={formData.service_date}
            onChange={handleChange}
            required
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="service_type">Tipo de Serviço *</label>
          <input
            type="text"
            id="service_type"
            name="service_type"
            value={formData.service_type}
            onChange={handleChange}
            placeholder="Ex: Instalação de Ar Condicionado"
            required
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="volatility_level">Flexibilidade do Cliente *</label>
          <select
            id="volatility_level"
            name="volatility_level"
            value={formData.volatility_level}
            onChange={handleChange}
            className="form-control"
          >
            <option value="low">Baixa (Difícil reagendar)</option>
            <option value="medium">Média (Aceita sugestões)</option>
            <option value="high">Alta (Fácil reagendar)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="required_tools">Ferramentas Necessárias (separadas por vírgula)</label>
          <input
            type="text"
            id="required_tools"
            name="required_tools"
            value={formData.required_tools}
            onChange={handleChange}
            placeholder="Ex: Chave de fenda, Escada, Furadeira"
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="observations">Observações</label>
          <textarea
            id="observations"
            name="observations"
            value={formData.observations}
            onChange={handleChange}
            placeholder="Detalhes adicionais sobre o serviço..."
            rows="3"
            className="form-control"
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Salvando...' : (initialData ? 'Atualizar Agendamento' : 'Criar Agendamento')}
        </button>
      </form>
    </div>
  );
};

export default AppointmentForm;