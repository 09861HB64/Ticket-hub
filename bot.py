from flask import Flask, render_template, jsonify, request
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard do Bot</title>
        <style>
            body { 
                font-family: Arial; 
                background: #0a0a0a; 
                color: white; 
                margin: 0; 
                padding: 20px; 
            }
            .container { 
                max-width: 1200px; 
                margin: auto; 
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; 
                border-radius: 15px; 
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: #1a1a1a;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #333;
            }
            .stat-card h3 {
                margin: 0;
                color: #667eea;
                font-size: 2em;
            }
            .search {
                width: 100%;
                padding: 15px;
                margin-bottom: 30px;
                background: #1a1a1a;
                border: 2px solid #333;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                transition: all 0.3s;
            }
            .search:focus {
                outline: none;
                border-color: #667eea;
            }
            .servidor {
                background: #1a1a1a;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                border: 1px solid #333;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .servidor:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                border-color: #667eea;
            }
            .servidor img {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                margin-right: 20px;
                border: 3px solid #667eea;
            }
            .info {
                flex: 1;
            }
            .info h3 {
                margin: 0 0 5px 0;
                font-size: 1.3em;
            }
            .info p {
                margin: 0;
                color: #888;
            }
            .btn {
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin: 5px;
                font-weight: bold;
                transition: all 0.3s;
            }
            .btn-danger {
                background: #e74c3c;
                color: white;
            }
            .btn-danger:hover {
                background: #c0392b;
                transform: scale(1.05);
            }
            .badge {
                background: #27ae60;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                display: inline-block;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Dashboard do Bot de Tickets</h1>
                <p>Gerencie todos os servidores onde o bot está</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3 id="totalServidores">0</h3>
                    <p>Total de Servidores</p>
                </div>
                <div class="stat-card">
                    <h3 id="totalMembros">0</h3>
                    <p>Membros Totais</p>
                </div>
            </div>
            
            <input type="text" class="search" id="search" placeholder="🔍 Buscar servidor por nome ou ID...">
            
            <div id="servidores"></div>
        </div>
        
        <script>
            let todosServidores = [];
            
            async function carregarServidores() {
                const response = await fetch('/api/servidores');
                todosServidores = await response.json();
                atualizarStats();
                renderizarServidores(todosServidores);
            }
            
            function atualizarStats() {
                document.getElementById('totalServidores').textContent = todosServidores.length;
                const totalMembros = todosServidores.reduce((acc, s) => acc + (s.membros || 0), 0);
                document.getElementById('totalMembros').textContent = totalMembros.toLocaleString();
            }
            
            function renderizarServidores(servidores) {
                const div = document.getElementById('servidores');
                div.innerHTML = '';
                
                servidores.forEach(s => {
                    div.innerHTML += `
                        <div class="servidor">
                            <img src="${s.icone || 'https://cdn.discordapp.com/embed/avatars/0.png'}" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                            <div class="info">
                                <h3>${s.nome}</h3>
                                <p>ID: ${s.id}</p>
                                <p>👥 ${s.membros || 0} membros</p>
                                <span class="badge">${s.ativo ? '✅ Ativo' : '❌ Inativo'}</span>
                            </div>
                            <div>
                                <button class="btn btn-danger" onclick="excluirServidor(${s.id})">🗑️ Remover Bot</button>
                            </div>
                        </div>
                    `;
                });
            }
            
            async function excluirServidor(id) {
                if(confirm('⚠️ Tem certeza que quer remover o bot deste servidor?\nO bot sairá do servidor e todos os dados serão perdidos!')) {
                    const response = await fetch(`/api/servidor/${id}/excluir`, {method: 'POST'});
                    const data = await response.json();
                    if(data.success) {
                        alert('✅ Bot removido do servidor com sucesso!');
                        carregarServidores();
                    }
                }
            }
            
            document.getElementById('search').addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                const filtrados = todosServidores.filter(s => 
                    s.nome.toLowerCase().includes(q) || 
                    s.id.toString().includes(q)
                );
                renderizarServidores(filtrados);
            });
            
            carregarServidores();
        </script>
    </body>
    </html>
    '''

@app.route('/api/servidores')
def get_servidores():
    conn = get_db()
    servidores = conn.execute('SELECT * FROM servidores').fetchall()
    return jsonify([dict(s) for s in servidores])

@app.route('/api/servidor/<int:server_id>/excluir', methods=['POST'])
def excluir_servidor(server_id):
    conn = get_db()
    conn.execute('DELETE FROM servidores WHERE id = ?', (server_id,))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/buscar')
def buscar_servidores():
    query = request.args.get('q', '')
    conn = get_db()
    servidores = conn.execute(
        'SELECT * FROM servidores WHERE nome LIKE ? OR id LIKE ?',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    return jsonify([dict(s) for s in servidores])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)