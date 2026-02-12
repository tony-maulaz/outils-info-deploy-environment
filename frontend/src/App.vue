<template>
  <main class="page">
    <header class="hero">
      <div>
        <h1>FastAPI + Vue + SQLite</h1>
        <p class="subtitle">Gestion d'environnements Docker Compose</p>
      </div>
      <div class="env">Env: {{ env }}</div>
    </header>

    <section class="card">
      <h2>API Health</h2>
      <div class="health">
        <span>Status: {{ health.status }}</span>
        <span>Env: {{ health.env }}</span>
        <span>DB: {{ health.db }}</span>
      </div>
      <button class="btn" @click="loadHealth">Rafraîchir</button>
    </section>

    <section class="card">
      <h2>Items</h2>
      <div class="token-row">
        <button class="btn" @click="loadToken">Charger token</button>
        <span class="token-value">Token: {{ token || '—' }}</span>
      </div>
      <div class="row">
        <input v-model="newItem" placeholder="Nouvel item" />
        <button class="btn" @click="addItem">Ajouter</button>
      </div>
      <ul class="list">
        <li v-for="item in items" :key="item.id">#{{ item.id }} - {{ item.name }}</li>
      </ul>
      <div class="hint">
        Le POST nécessite l'en-tête <code>Authorization: Bearer &lt;token&gt;</code>.
      </div>
    </section>

    <footer class="foot">
      <span>VITE_API_URL: {{ apiUrl }}</span>
    </footer>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || ''
const env = import.meta.env.VITE_APP_ENV || 'dev'

const health = ref({ status: '...', env: '...', db: '...' })
const items = ref([])
const newItem = ref('')
const token = ref(localStorage.getItem('jwt_token') || '')

async function loadHealth() {
  const res = await fetch(`${apiUrl}/api/health`)
  health.value = await res.json()
}

async function loadItems() {
  const res = await fetch(`${apiUrl}/api/items`)
  items.value = await res.json()
}

async function addItem() {
  if (!newItem.value.trim()) return
  const tokenValue = localStorage.getItem('jwt_token') || ''
  const headers = {
    'Content-Type': 'application/json'
  }
  if (tokenValue) {
    headers.Authorization = `Bearer ${tokenValue}`
  }
  const res = await fetch(`${apiUrl}/api/items`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ name: newItem.value })
  })

  if (res.ok) {
    newItem.value = ''
    await loadItems()
  } else {
    const err = await res.json().catch(() => ({}))
    alert(err.detail || 'Erreur')
  }
}

async function loadToken() {
  const res = await fetch(`${apiUrl}/api/token`)
  if (res.ok) {
    const data = await res.json()
    token.value = data.token || ''
    if (token.value) {
      localStorage.setItem('jwt_token', token.value)
    }
  } else {
    const err = await res.json().catch(() => ({}))
    alert(err.detail || 'Erreur')
  }
}

onMounted(async () => {
  await loadHealth()
  await loadItems()
})
</script>

<style scoped>
:root {
  color-scheme: light;
}

.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
  font-family: "Segoe UI", system-ui, sans-serif;
  color: #1b1b1b;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border-bottom: 2px solid #eee;
  padding-bottom: 16px;
}

.subtitle {
  color: #666;
  margin-top: 4px;
}

.env {
  background: #0b4f6c;
  color: #fff;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 600;
}

.card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
}

.health {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.token-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.token-value {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New",
    monospace;
  font-size: 12px;
  color: #374151;
}

input {
  flex: 1;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
}

.btn {
  background: #0b4f6c;
  color: #fff;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  padding: 6px 0;
  border-bottom: 1px dashed #ddd;
}

.hint {
  margin-top: 10px;
  color: #666;
}

.foot {
  margin-top: 20px;
  font-size: 12px;
  color: #666;
}
</style>
