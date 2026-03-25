# 🎤 Assistente de Voz Multi-Idiomas com Whisper e Groq

Um assistente de voz inteligente que captura áudio, transcreve usando Whisper, processa a solicitação com IA via Groq e responde sintetizando a voz.

## 🚀 Funcionalidades

- **Gravação de Áudio**: Captura áudio do microfone em tempo real
- **Transcrição Automática**: Reconhece fala em múltiplos idiomas com Whisper
- **IA Inteligente**: Processa requisições via API Groq (modelo Llama 3.3)
- **Síntese de Voz**: Converte resposta em áudio natural com gTTS
- **Multi-idioma**: Suporta diversos idiomas para entrada e saída

## 📋 Pré-requisitos

- Python 3.8+
- Microfone funcional
- API Key do Groq (obtenha em https://console.groq.com/keys)

## 📦 Dependências

```bash
Todas as dependências estão nas células acima do bloco que são utilizadas.
```

## ⚙️ Como Usar

1. Configure sua API Key do Groq no notebook
2. Execute as células na sequência:
   - Gravação de áudio (5 segundos padrão)
   - Transcrição com Whisper
   - Integração com Groq para processar texto
   - Síntese e reprodução da resposta em voz

## 🛫 Próximos Passos

- [ ] Implementar interface gráfica
- [ ] Adicionar suporte a diferentes modelos de IA via seleção dinâmica
- [ ] Salvar histórico de conversas em banco de dados
- [ ] Otimizar tempo de resposta com cache
- [ ] Implementar detecção de idioma automática
- [ ] Adicionar tratamento robusto de erros
- [ ] Criar CLI para uso em terminal

## 💡 Possibilidades de Expansão

- **Assistente Pessoal**: Integrar com calendário, tarefas e emails
- **Suporte a Plugins**: Sistema de extensões para funcionalidades customizadas
- **Web App**: Deploy como API REST com frontend
- **Voice Commands**: Configurar comandos específicos de voz para ações locais
- **Histórico Inteligente**: Memória de conversa com contexto persistente
- **Integração com APIs**: Conectar a serviços externos (previsão, notícias, etc.)
- **Offline Mode**: Utilizar modelos locais para privacidade
- **Multilíngue Avançado**: Tradução automática entre idiomas


## 🔧 Configuração da API

Obtenha sua chave em: https://console.groq.com/keys


## 📄 Licença

Este projeto é um exercício educacional da DIO em parceria com Bradesco.
