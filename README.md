# Maxfrio - Sistema de Agendamento com IA

Sistema de agendamento de serviços para a Maxfrio com assistente de IA para reagendamento e recomendações.

## Estrutura do Projeto

```
agendamento_max/
├── backend/                 # API FastAPI com Python
│   ├── src/
│   │   ├── api/         # Rotas da API e middleware
│   │   ├── models/       # Modelos de dados (Appointment, Occurrence)
│   │   ├── services/     # Lógica de negócio (storage, AI)
│   │   ├── main.py       # Ponto de entrada da aplicação
│   │   └── config.py      # Configurações
│   ├── data/              # Armazenamento de dados
│   │   └── appointments.txt
│   └── requirements.txt     # Dependências Python
├── frontend/               # Aplicação React
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── pages/        # Páginas da aplicação
│   │   ├── services/     # Comunicação com API
│   │   ├── styles/       # Estilos CSS
│   │   ├── main.jsx      # Ponto de entrada React
│   │   └── App.jsx        # Componente principal
│   ├── public/             # Arquivos estáticos
│   ├── package.json         # Dependências Node.js
│   └── vite.config.js       # Configuração Vite
├── scripts/                # Scripts de automação
│   ├── setup.ps1           # Configuração inicial
│   ├── start-backend.ps1     # Iniciar backend
│   └── start-frontend.ps1    # Iniciar frontend
└── specs/                 # Especificações do sistema
    └── 001-ai-scheduling/
```

## Configuração Inicial

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- PowerShell (Windows)

### Instalação

1. Execute o script de configuração:
   ```powershell
   .\scripts\setup.ps1
   ```

Este script irá:
- Criar ambiente virtual Python
- Instalar dependências do backend
- Instalar dependências do frontend
- Criar arquivo .env para configuração da API Google

2. Configure a chave da API Google:
   - Edite o arquivo `.env` na raiz do projeto
   - Substitua `your_api_key_here` pela sua chave da API Google Gemini

## Execução

### Iniciar o Backend

```powershell
.\scripts\start-backend.ps1
```

O backend estará disponível em: http://localhost:8000

### Iniciar o Frontend

```powershell
.\scripts\start-frontend.ps1
```

O frontend estará disponível em: http://localhost:3000

## Funcionalidades

### Fase 1: Configuração (Completo)
- ✅ Estrutura do projeto criada
- ✅ Backend FastAPI configurado
- ✅ Frontend React configurado
- ✅ Scripts de automação criados
- ✅ Armazenamento de dados inicializado

### Próximas Fases

A implementação das User Stories seguirá esta ordem:

1. **User Story 1 - Criação Manual de Agendamentos**
   - Formulário para criar novos agendamentos
   - Validação de dados
   - Exibição de agendamentos criados

2. **User Story 2 - Gestão Visual de Agendamentos**
   - Cards coloridos por status
   - Ordenação por prioridade
   - Funcionalidade de edição

3. **User Story 3 - Assistente de IA para Reagendamento**
   - Chat em linguagem natural
   - Recomendações de serviços
   - Reagendamento automático

4. **User Story 4 - Conclusão de Serviços e Gestão de Ocorrências**
   - Marcar serviços como concluídos
   - Histórico de alterações
   - Preservação de registros

## API Documentation

A documentação automática da API estará disponível em:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Estrutura de Dados

Os agendamentos são armazenados em formato JSON no arquivo `backend/data/appointments.txt`:

```json
{
  "appointments": [
    {
      "id": "uuid",
      "customer_name": "Nome do Cliente",
      "service_date": "2025-12-10T14:30:00",
      "service_type": "Tipo de Serviço",
      "volatility_level": "low|medium|high",
      "observations": "Observações",
      "required_tools": ["Ferramenta 1", "Ferramenta 2"],
      "status": "pending|in_progress|completed",
      "created_at": "2025-12-09T10:00:00",
      "updated_at": "2025-12-09T10:00:00",
      "occurrences": []
    }
  ],
  "metadata": {
    "last_updated": "2025-12-09T14:30:00",
    "version": "1.0",
    "total_appointments": 1
  }
}
```

## Estilos e Design

- **Cores**: Esquema azul conforme especificação
- **Acessibilidade**: Conformidade WCAG 2.1 AA
- **Responsividade**: Mobile-first com breakpoints para desktop e mobile
- **Tipografia**: Fontes grandes para usuários 50+

## Desenvolvimento

### Ambiente Virtual Python

```powershell
# Ativar ambiente virtual
.\backend\venv\Scripts\Activate
```

### Instalar Dependências

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Logs

- Logs do backend: `backend/logs/api.log`
- Logs de erro: Exibidos no console do navegador

## Contribuição

1. Seguir a estrutura de pastas definida
2. Manter conformidade com as especificações em `specs/001-ai-scheduling/`
3. Testar funcionalidades antes de submeter alterações
4. Documentar novas funcionalidades

## Licença

Projeto interno para uso da Maxfrio.