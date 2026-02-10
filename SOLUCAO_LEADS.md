# 🔧 SOLUÇÃO: CARREGAR LEADS DA API

## ❌ PROBLEMA IDENTIFICADO

O arquivo `index.html` tem a função `loadComercialKanbanData()` que **só lê do LocalStorage**, não busca os leads do backend (`/api/leads`).

Quando o computador desligou, o LocalStorage foi limpo → **leads desapareceram**.

---

## ✅ SOLUÇÃO

Preciso adicionar uma função que carregue os leads da API ao abrir a seção comercial.

### Código a adicionar (em index.html):

```javascript
// Adicionar LOGO APÓS a função initComercialKanban():

// Carregar leads do backend ao abrir comercial
async function loadLeadsFromBackend() {
    try {
        const response = await fetch('/api/leads');
        const leads = await response.json();
        
        if (!Array.isArray(leads) || leads.length === 0) {
            console.log('Nenhum lead encontrado');
            return;
        }
        
        // Encontrar coluna "Entrada de Lead"
        const entradaColumn = document.querySelector('[data-column-title="Entrada de Lead"]');
        if (!entradaColumn) return;
        
        // Adicionar cada lead como card
        leads.forEach(lead => {
            // Verificar se card já existe
            if (document.querySelector(`[data-lead-id="${lead.id}"]`)) return;
            
            const card = document.createElement('div');
            card.className = 'kanban-card';
            card.setAttribute('data-lead-id', lead.id);
            card.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div style="flex:1;">
                        <h4 style="margin:0 0 8px 0;color:#0E4D42;font-size:14px;">Lead #${lead.id}</h4>
                        <p style="margin:0 0 4px 0;font-size:12px;color:#666;"><strong>Responsável:</strong> ${lead.responsible_user || 'N/A'}</p>
                        <p style="margin:0 0 8px 0;font-size:12px;color:#666;"><strong>Fonte:</strong> ${lead.lead_source || 'N/A'}</p>
                        <small style="color:#999;">Criado: ${new Date(lead.created_at).toLocaleDateString('pt-BR')}</small>
                    </div>
                    <button class="btn-delete-card" style="background:none;border:none;color:#d32f2f;cursor:pointer;font-size:18px;" onclick="deleteLead('${lead.id}')">×</button>
                </div>
            `;
            entradaColumn.appendChild(card);
        });
        
    } catch (error) {
        console.error('Erro ao carregar leads:', error);
    }
}

// Função para deletar lead
async function deleteLead(leadId) {
    if (confirm('Deletar este lead?')) {
        const response = await fetch(`/api/leads/${leadId}`, { method: 'DELETE' });
        if (response.ok) {
            document.querySelector(`[data-lead-id="${leadId}"]`).remove();
            alert('Lead deletado com sucesso!');
        }
    }
}

// Chamar ao inicializar comercial
function initComercialKanban() {
    loadComercialKanbanData();
    loadLeadsFromBackend();  // ← ADICIONAR ESTA LINHA
}
```

---

## 📝 ONDE ADICIONAR

1. Abra `index.html`
2. Procure por: `function initComercialKanban()`
3. Logo depois de `loadComercialKanbanData();` adicione: `loadLeadsFromBackend();`
4. Copie a função `loadLeadsFromBackend()` acima (antes de fechar o script)
5. Salve o arquivo
6. Reinicie a aplicação: `python app.py`

---

## 🧪 TESTE

1. Acesse: `http://localhost:5000`
2. Faça login
3. Vá em: Administrativo → Comercial
4. Clique em: "Novo Lead"
5. Preencha: Responsável e Fonte
6. Clique: "Criar Lead"
7. **O card deve aparecer em "Entrada de Lead"** ✅

---

## 💡 ALTERNATIVA RÁPIDA (Se não quiser editar)

Se não quiser editar o HTML, teste criando um lead via curl:

```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"responsible_user":"Gabriela","lead_source":"teste"}'
```

Depois recarregue a página comercial.

---

**Tente esta solução e me avise se funcionar! 💪**
