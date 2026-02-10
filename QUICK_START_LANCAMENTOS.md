# 🚀 QUICK START - MÓDULO LANÇAMENTOS

**⏱️ Tempo de leitura**: 5 minutos  
**👥 Público**: Usuários finais e desenvolvedores  
**🎯 Objetivo**: Começar a usar AGORA

---

## 1️⃣ INICIAR O SISTEMA

### Opção A: Automático (Recomendado)
```bash
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON"
double-click INICIAR_SERVIDOR.bat
```

### Opção B: Manual
```bash
# Terminal PowerShell
python app.py
# Ou
python3 app.py
```

### ✅ Confirmação
Deve aparecer:
```
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

---

## 2️⃣ ACESSAR LANÇAMENTOS

1. Abrir navegador: **http://localhost:5000**
2. Clique em **"Financeiro"** (no menu)
3. Procure a aba **"Lançamentos"** (última antes de Relatórios)
4. Você verá uma tabela vazia (primeira vez)

---

## 3️⃣ ENTRAR PRIMEIRA TRANSAÇÃO

### Passo a Passo

```
1. Clique em "+ Novo Lançamento"
   ↓
2. Preencha o formulário:
   • Data Competência: hoje (auto-preenchido)
   • Data Vencimento: hoje + 30 dias (auto-preenchido)
   • Centro de Custo: "Setores Operacionais"
   • Cliente/Fornecedor: "João da Silva"
   • Instituição: "Clínica"
   • Forma de Pagamento: "Dinheiro"
   • Categoria: "Receita com serviços"
   • Subcategoria: "Consulta Presencial" (auto-ajusta)
   • Descrição: "Consulta Dr. Pedro"
   • Valor: 150.00
   • Data Extrato: hoje
   • Status: "Lançado"
   ↓
3. Clique em "Salvar"
   ↓
4. Pronto! Lançamento aparece na tabela
```

### Exemplo de Transação Completa

| Campo | Exemplo |
|---|---|
| Data Competência | 04/02/2026 |
| Data Vencimento | 06/03/2026 |
| Centro de Custo | Setores Operacionais |
| Cliente | Maria Silva |
| Instituição | Clínica |
| Forma Pagamento | PIX |
| Categoria | Receita com serviços |
| Subcategoria | Consulta Presencial |
| Descrição | Consulta Dr. Ricardo |
| Valor | 150,00 |
| Data Extrato | 04/02/2026 |
| Status | Conciliado |

---

## 4️⃣ USANDO FILTROS

### Filtrar por Período

```
1. Preencha "Data Início": 01/02/2026
2. Preencha "Data Fim": 28/02/2026
3. Clique "Filtrar"
4. Tabela mostra só lançamentos de fevereiro
```

### Filtrar por Centro de Custo

```
1. Selecione no dropdown: "Setores Operacionais"
2. Clique "Filtrar"
3. Tabela mostra só desse centro
```

### Filtrar por Status

```
1. Selecione: "Conciliado"
2. Clique "Filtrar"
3. Tabela mostra só conciliados
```

### Combinar Filtros

```
Todos os 3 filtros funcionam juntos:
- Data: 01/02 a 28/02
- Centro: Setores Operacionais
- Status: Conciliado
= Mostra só as transações que atendem TODOS os critérios
```

---

## 5️⃣ EXPORTAR PARA EXCEL

### Como Fazer

```
1. Clique em "Exportar" (botão verde)
2. Arquivo baixa automaticamente:
   lancamentos_2026-02-04_14-30-45.csv
3. Abra em Excel/Planilha
4. Pronto para análise!
```

### O que Exporta

- ✅ Todas as colunas
- ✅ Todos os lançamentos atuais
- ✅ Respeitando filtros aplicados
- ✅ Formato CSV (compatível com Excel)

---

## 6️⃣ ENTENDER O RESUMO

O resumo mostra 3 números importantes:

### 🟢 Total Receitas
```
Soma de todos os lançamentos com categoria que começa com "Receita"
Exemplo: 
  - Consulta: R$ 150
  - Venda Produto: R$ 50
  = Total: R$ 200
```

### 🔴 Total Despesas
```
Soma de todos os lançamentos com categoria que começa com "Despesa"
Exemplo:
  - Medicamento: R$ 30
  - Aluguel: R$ 1.000
  = Total: R$ 1.030
```

### 💚 Resultado
```
Receitas - Despesas
Exemplo: R$ 200 - R$ 1.030 = -R$ 830 (NEGATIVO = vermelho)
         R$ 2.000 - R$ 1.000 = R$ 1.000 (POSITIVO = verde)
```

---

## 7️⃣ CATEGORIAS DISPONÍVEIS

### Receitas

```
✅ Receita com produtos
   └─ Fitorerapico, Microbiota, Probióticos, Suplementos, Outros

✅ Receita com serviços
   └─ Consulta Online, Consulta Presencial, Nutricionista, 
      Dentista, Consulta Equipe, Plano Fidelidade, Outros
```

### Despesas

```
✅ Despesas Operacionais
   └─ Matéria Prima, Salários, Aluguel, Utilidades, Manutenção

✅ Despesas Administrativas
   └─ Escritório, Licenças, Seguros, Consultoria

✅ Despesas Financeiras
   └─ Juros, Emolumentos Bancários, Taxas

✅ Deduções
   └─ Devolução de Produto, Cancelamento de Serviço, Desconto Oferecido
```

---

## 8️⃣ STATUS DE LANÇAMENTO

### 🟢 Lançado
- Significado: Registrado mas não confirmado
- Usar para: Consultas não pagas, vendas pendentes
- Ação: Mudar para "Conciliado" após pagamento

### 🔵 Conciliado
- Significado: Confirmado (pagamento recebido/realizado)
- Usar para: Consultas pagas, compras confirmadas
- Ação: Nenhuma (transação fechada)

### 🟠 Pendente
- Significado: Aguardando ação
- Usar para: Faturas vencidas, pagamentos pendentes
- Ação: Cobrar ou resolver

---

## 9️⃣ DICAS E TRUQUES

### ✅ Dica 1: Datas Automáticas
```
Ao criar novo lançamento:
- "Data Competência" já vem com HOJE
- "Data Vencimento" já vem com HOJE + 30 dias
- Você pode mudar se necessário
```

### ✅ Dica 2: Subcategorias Mudam Automaticamente
```
1. Selecione uma Categoria
2. Subcategorias mudam automaticamente
3. Subcategoria sempre válida para a categoria
```

### ✅ Dica 3: Filtros Limpam
```
Para limpar filtros:
1. Deixe campos vazios
2. Selecione "--- Selecione ---"
3. Clique "Filtrar"
4. Tabela volta a mostrar TUDO
```

### ✅ Dica 4: Deletar É Rápido
```
Para deletar um lançamento:
1. Clique ícone de lixeira (🗑️) na linha
2. Confirme "Você tem certeza?"
3. Pronto, deletado imediatamente
4. Resumo atualiza automaticamente
```

### ✅ Dica 5: Dados Salvam Automaticamente
```
Não precisa salvar:
- localStorage salva automáticamente
- Mesmo se fechar aba, dados continuam
- Mesmo se desligar computador, dados ficam
- (até limpar cache do navegador)
```

---

## 🔟 PROBLEMAS E SOLUÇÕES

### ❌ "Tabela está vazia"
**Solução**: Crie seu primeiro lançamento:
1. Clique "+ Novo Lançamento"
2. Preencha com dados de exemplo
3. Clique "Salvar"

### ❌ "Não consigo salvar"
**Solução**: Verifique:
1. Todos os campos foram preenchidos?
2. Valor é um número válido?
3. Categorias estão nas opções?
4. Abrir F12 → Console para ver erro

### ❌ "Desapareceu meu lançamento"
**Solução**: Possíveis causas:
1. Filtro ativo escondendo → Desativar filtros
2. Limpou cache → Restaurar dados
3. localStorage cheio → Deletar alguns antigos

### ❌ "Resumo está errado"
**Solução**: 
1. Verificar categorias dos lançamentos
2. Categorias que começam com "Receita" = receitas
3. Categorias que começam com "Despesa" = despesas
4. Recarregar página (Ctrl+R)

### ❌ "Não consigo exportar"
**Solução**: 
1. Verificar se o navegador permite downloads
2. Verificar pasta Downloads
3. Tentar outro navegador
4. Abrir console (F12) para erros

---

## 1️⃣1️⃣ EXEMPLOS PRONTOS

### Exemplo 1: Consulta (Receita)
```
Data Competência: 04/02/2026
Data Vencimento: 06/03/2026
Centro de Custo: Setores Operacionais
Cliente: Maria Silva
Instituição: Clínica
Forma Pagamento: PIX
Categoria: Receita com serviços
Subcategoria: Consulta Presencial
Descrição: Consulta com Dr. João
Valor: 150.00
Status: Conciliado
```

### Exemplo 2: Medicamento (Despesa)
```
Data Competência: 04/02/2026
Data Vencimento: 04/02/2026
Centro de Custo: Setores Operacionais
Cliente: Estoque
Instituição: Farmácia
Forma Pagamento: Cheque
Categoria: Despesas Operacionais
Subcategoria: Matéria Prima
Descrição: Amoxicilina 500mg (20 unidades)
Valor: 10.00
Status: Lançado
```

### Exemplo 3: Aluguel (Despesa)
```
Data Competência: 01/02/2026
Data Vencimento: 01/02/2026
Centro de Custo: Setores Operacionais
Cliente: Imobiliária XYZ
Instituição: Banco
Forma Pagamento: Transferência
Categoria: Despesas Operacionais
Subcategoria: Aluguel
Descrição: Aluguel de fevereiro - Sala principal
Valor: 2000.00
Status: Conciliado
```

---

## 1️⃣2️⃣ AUTOMAÇÃO (FUTURO)

### O Que Vai Acontecer

Quando o sistema de pacientes estiver pronto:

```
Paciente faz Consulta
    ↓
Sistema cria Lançamento automaticamente
    ↓
Você não precisa digitar nada
    ↓
Tudo aparece em Lançamentos
```

### Operações Que Serão Automáticas

- ✅ Consulta → Cria receita
- ✅ Medicamento → Cria despesa
- ✅ Pagamento → Concilia lançamento
- ✅ Produto → Cria receita

---

## 🎯 PRÓXIMAS LEITURAS

### Se quer...

| Objetivo | Arquivo |
|---|---|
| Entender estrutura completa | [MODULO_LANCAMENTOS.md](MODULO_LANCAMENTOS.md) |
| Saber como será automação | [AUTOMACAO_LANCAMENTOS.md](AUTOMACAO_LANCAMENTOS.md) |
| Integrar com seu código | [EXEMPLO_INTEGRACAO_LANCAMENTOS.md](EXEMPLO_INTEGRACAO_LANCAMENTOS.md) |
| Testar funcionalidades | [TESTES_LANCAMENTOS.md](TESTES_LANCAMENTOS.md) |
| Ver detalhes técnicos | [RELATORIO_FINAL_LANCAMENTOS.md](RELATORIO_FINAL_LANCAMENTOS.md) |

---

## 📞 SUPORTE RÁPIDO

### Problema no Console?
```
Abra F12 ou Ctrl+Shift+K
Veja mensagem de erro
Procure aqui: TESTES_LANCAMENTOS.md → Troubleshooting
```

### Precisa Integrar?
```
Vá a: EXEMPLO_INTEGRACAO_LANCAMENTOS.md
Copie o hook correspondente
Cole em seu código
Teste com dados de exemplo
```

### Quer Customizar?
```
Edite index.html
Procure por "Lançamentos" (Ctrl+F)
Veja comentários no código
Teste mudanças localmente
```

---

## ✅ Checklist - Primeira Execução

- [ ] Servidor iniciado (http://localhost:5000)
- [ ] Página de Financeiro carregou
- [ ] Aba "Lançamentos" visível
- [ ] Botão "+ Novo Lançamento" funciona
- [ ] Formulário abre sem erros
- [ ] Conseguiu criar primeiro lançamento
- [ ] Lançamento aparece na tabela
- [ ] Resumo atualizou com o valor
- [ ] Filtro funcionou
- [ ] Export baixou arquivo CSV

---

## 🎉 Parabéns!

Você já sabe o básico de Lançamentos! 

### Próximas ações:

1. **Experimente**: Crie mais alguns lançamentos com diferentes categorias
2. **Teste filtros**: Pratique filtrar por período, centro, status
3. **Exporte**: Abra um CSV em Excel e explore
4. **Customize**: Se precisar, estude o arquivo [MODULO_LANCAMENTOS.md](MODULO_LANCAMENTOS.md)
5. **Integre**: Quando tiver sistema de pacientes, consulte [EXEMPLO_INTEGRACAO_LANCAMENTOS.md](EXEMPLO_INTEGRACAO_LANCAMENTOS.md)

---

## 🚀 Dica Final

**Comece simples:**
1. Crie 5 lançamentos de teste
2. Experimente cada filtro
3. Exporte e veja em Excel
4. Depois explore funcionalidades mais avançadas

**Boa sorte!** 🎯

---

**Versão**: 1.0  
**Data**: 04 de Fevereiro de 2026  
**Tempo de Leitura**: ⏱️ ~5 minutos  
**Pronto para Usar**: ✅ SIM!
