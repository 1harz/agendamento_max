import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import './styles/components.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Maxfrio - Sistema de Agendamento</h1>
        <p>Gerenciamento de serviços com assistente de IA</p>
      </header>
      
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  )
}

export default App