# 🎯 GUIA RÁPIDO - VISUALIZANDO AS MUDANÇAS

## ⚡ ACESSO RÁPIDO

### 1️⃣ Abra o navegador
```
http://localhost:5000
```

### 2️⃣ Clique em "Financeiro" (menu lateral)

### 3️⃣ Você verá 6 abas - Clique em:
- **"Centros de Custo"** - Para ver a estrutura hierárquica
- **"Plano de Contas"** - Para ver receitas e despesas

---

## 📺 O QUE VOCÊ VERÁ

### Na Aba "Centros de Custo"

Você verá **3 grupos principais**, cada um com seus subgrupos:

```
┌─────────────────────────────────────────────────────┐
│ PRODUTOS, SERVIÇOS OU CONTRATOS        ⚙️          │
├──────────────────┬─────────────────────────────────┤
│ Subgrupo         │ Status                          │
├──────────────────┼─────────────────────────────────┤
│ Médicos          │ ✓ Ativo                         │
│ Clínica Verde    │ ✓ Ativo                         │
│ Dentista         │ ✓ Ativo                         │
│ Holding Espaço   │ ✓ Ativo                         │
│ Nutricionista    │ ✓ Ativo                         │
│ Nutriquantum     │ ✓ Ativo                         │
│ ON Medicina      │ ✓ Ativo                         │
│ Quantulab        │ ✓ Ativo                         │
│ Tricologia       │ ✓ Ativo                         │
└──────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SETORES OPERACIONAIS                   ⚙️          │
├──────────────────┬─────────────────────────────────┤
│ Subgrupo         │ Status                          │
├──────────────────┼─────────────────────────────────┤
│ Atendimento Dom. │ ✓ Ativo                         │
│ Atendimento Op.  │ ✓ Ativo                         │
│ Unidade Conceito │ ✓ Ativo                         │
│ Telemedicina     │ ✓ Ativo                         │
│ Importação Prod. │ ✓ Ativo                         │
└──────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SETORES DA ADMINISTRAÇÃO                ⚙️         │
├──────────────────┬─────────────────────────────────┤
│ Subgrupo         │ Status                          │
├──────────────────┼─────────────────────────────────┤
│ Setor Admin.     │ ✓ Ativo                         │
│ Setor Ativo Cons.│ ✓ Ativo                         │
│ Setor Contabil.  │ ✓ Ativo                         │
│ Setor Jurídico   │ ✓ Ativo                         │
│ Setor Manutenção │ ✓ Ativo                         │
└──────────────────┴─────────────────────────────────┘
```

### Na Aba "Plano de Contas"

Você verá **receitas e despesas organizadas** por categoria:

```
┌────────────────┬─────────────┬──────────────────┬───────────┐
│ Grupo          │ Categoria   │ Subcategoria     │ Status    │
├────────────────┼─────────────┼──────────────────┼───────────┤
│ Receita Bruta  │ Receita com │ Receita com      │ Ativo     │
│                │ produtos e  │ produtos e       │ Exibido   │
│                │ mercadorias │ mercadorias      │           │
│                │             │                  │           │
│                │             │ Fitorerapico     │ Ativo     │
│                │             │ Microbiota       │ Exibido   │
│                │             │ Mitocondria      │ Ativo     │
│                │             │ Mulher           │ Exibido   │
│                │             │                  │           │
│ Receita Bruta  │ Receita com │ Receita com      │ Ativo     │
│                │ prestação   │ prestação de     │ Exibido   │
│                │ de serviços │ serviços         │           │
│                │             │                  │           │
│                │             │ Consulta Equipe  │ Ativo     │
│                │             │ Consulta Online  │ Exibido   │
│                │             │ Consulta Presenc.│ Ativo     │
│                │             │ Dentista         │ Exibido   │
│                │             │ Nutricionista    │ Ativo     │
│                │             │ Plano Fidelidade │ Exibido   │
│                │             │ (Plus, Rara,     │           │
│                │             │  Personalité)    │           │
│                │             │ Plano Plus       │ Ativo     │
│                │             │ Plano Veterinário│ Exibido   │
│                │             │ Sessão Presenc.  │ Ativo     │
│                │             │ Tricologia       │ Exibido   │
│                │             │                  │           │
│ Deduções da    │ Abatimentos │ Descontos        │ Ativo     │
│ Receita        │ e descontos │ Concedidos       │ Exibido   │
│                │             │ Abatimentos      │ Ativo     │
│                │             │ Devoluções       │ Exibido   │
│                │             │                  │           │
│ Despesas       │ Desp.       │ Pessoal Encargos │ Ativo     │
│                │ Operacional │ Aluguel          │ Exibido   │
│                │             │ Utilidades       │ Ativo     │
│                │             │ Matéria Prima    │ Exibido   │
│                │             │ Marketing        │ Ativo     │
│                │             │                  │ Exibido   │
│ Despesas       │ Desp.       │ Contabilidade    │ Ativo     │
│                │ Admin       │ Jurídico         │ Exibido   │
│                │             │ Consultoria      │ Ativo     │
│                │             │ Escritório       │ Exibido   │
│                │             │                  │           │
│ Despesas       │ Desp.       │ Juros Bancários  │ Ativo     │
│                │ Financeira  │ Taxa Serviço     │ Exibido   │
│                │             │ Multas Juros     │ Ativo     │
│                │             │                  │ Exibido   │
└────────────────┴─────────────┴──────────────────┴───────────┘
```

---

## 🔧 ESTRUTURA DE DADOS

### Centro de Custo
- Armazenado em: `data/centros_custo.json`
- Estrutura: **Grupos** → **Subgrupos**
- Propriedades: `id`, `nome`, `subgrupos[]`, `status`

### Plano de Contas
- Armazenado em: `data/plano_contas.json`
- Estrutura: **Grupos** → **Categorias** → **Subcategorias**
- Propriedades: `id`, `grupo`, `categoria`, `subcategorias[]`, `status`

---

## 💾 COMO EDITAR OS DADOS

Se você quiser **adicionar ou modificar** grupos/subgrupos:

### 1️⃣ Editar Centro de Custo
Abra: `data/centros_custo.json`

```json
{
  "grupos": [
    {
      "id": 1,
      "nome": "Produtos, serviços ou Contratos",
      "subgrupos": [
        {
          "id": 101,
          "nome": "Médicos",
          "status": "Ativo"
        },
        // Adicione novo subgrupo aqui:
        {
          "id": 110,
          "nome": "Novo Subgrupo",
          "status": "Ativo"
        }
      ]
    }
  ]
}
```

### 2️⃣ Editar Plano de Contas
Abra: `data/plano_contas.json`

```json
{
  "plano_contas": [
    {
      "id": 1,
      "grupo": "Receita Bruta",
      "categoria": "Receita com produtos e mercadorias",
      "subcategorias": [
        {
          "id": 101,
          "nome": "Receita com produtos e mercadorias",
          "status": "Ativo/Exibido"
        },
        // Adicione nova subcategoria aqui:
        {
          "id": 106,
          "nome": "Nova Subcategoria",
          "status": "Ativo/Exibido"
        }
      ]
    }
  ]
}
```

### 3️⃣ Salve e Recarregue
```
Ctrl + S  (para salvar)
F5        (para recarregar no navegador)
```

---

## ✅ VALIDAÇÃO

Para verificar se tudo está funcionando:

### No Navegador:
1. Pressione `F12` (Developer Tools)
2. Vá para a aba "Console"
3. Procure por mensagens de sucesso (não deve haver erros vermelhos)

### No Terminal:
```powershell
cd "C:\Users\Gabriela Resende\Documents\Plataforma ON"
python teste_estruturas.py
```

Resultado esperado:
```
✅ Arquivo centros_custo.json carregado
✅ Arquivo plano_contas.json carregado
✅ Total de grupos: 3
✅ Total de subcategorias: 33
```

---

## 🎨 ESTILOS E CORES

Os dados aparecem com:
- **Cabeçalhos em gradiente verde** (#0E4D42 → #4A7A6A)
- **Status em badges verdes** (Ativo/Exibido)
- **Tabelas com hover effects**
- **Design responsivo** (funciona em mobile também)

---

## 🚀 RECURSOS AVANÇADOS

### Buscar Dados Programaticamente

```javascript
// No Console (F12 → Console)

// Acessar dados de Centro de Custo
window.centrosCustoData

// Acessar dados de Plano de Contas
window.planoContasData

// Renderizar novamente
loadCentrosCustoTable()
loadPlanoContasTable()
```

---

## 📱 RESPONSIVIDADE

O módulo foi desenvolvido para funcionar em:
- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablet (iPad, Android tablets)
- ✅ Mobile (smartphones)

---

## 🆘 TROUBLESHOOTING

### Problema: Os dados não aparecem

**Solução:**
1. Abra o console (F12)
2. Procure por erros vermelhos
3. Recarregue a página (F5)
4. Certifique-se que os arquivos JSON estão em `data/`

### Problema: Mudanças não aparecem

**Solução:**
1. Salve o arquivo JSON (Ctrl + S)
2. Recarregue o navegador (Ctrl + Shift + R - reload com cache limpo)

### Problema: Erro "Arquivo não encontrado"

**Solução:**
1. Verifique se os arquivos estão em:
   - `data/centros_custo.json`
   - `data/plano_contas.json`
2. Reinicie o servidor (python app.py)

---

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique o console (F12)
2. Execute `teste_estruturas.py`
3. Verifique os arquivos JSON existem
4. Reinicie o servidor Flask

---

**Pronto para usar! 🚀**

Agora você tem uma estrutura clara e organizada de Centro de Custo
e Plano de Contas, exatamente como foi solicitado!
