async function fetchMenu(){
  const res = await fetch('/api/menu/');
  const data = await res.json();
  const container = document.getElementById('menu');
  container.innerHTML = '';
  if(data.error){ container.innerText = 'Error loading menu: ' + data.error; return; }
  const items = data.items || data;
  items.forEach(it => {
    const div = document.createElement('div');
    div.style.border='1px solid #ddd'; div.style.padding='10px'; div.style.margin='8px 0';
    div.innerHTML = `<strong>${it.name}</strong> - ${it.price}<br><small>${it.description||''}</small><br>`;
    const qty = document.createElement('input'); qty.type='number'; qty.value=1; qty.min=1; qty.style.width='60px';
    const btn = document.createElement('button'); btn.innerText='Add to cart';
    btn.onclick = () => addToCart(it, parseInt(qty.value||1));
    div.appendChild(qty); div.appendChild(btn);
    container.appendChild(div);
  });
}
async function addToCart(item, qty){
  const body = { action: 'add', item: { id: item.id, name: item.name, price: item.price, qty: qty } };
  const res = await fetch('/api/cart/', { method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify(body) });
  const data = await res.json(); renderCart(data.cart);
}
function renderCart(cart){
  const el = document.getElementById('cart-contents');
  if(!cart || cart.length===0){ el.innerText='Empty'; document.getElementById('cart-total').innerText='0'; return; }
  el.innerHTML=''; let total=0;
  cart.forEach(it=>{
    const row = document.createElement('div');
    row.innerHTML = `${it.name} x <input type="number" value="${it.qty}" min="1" style="width:60px" data-id="${it.id}"> = ${it.price*it.qty} <button data-id="${it.id}" class="remove-btn">Remove</button>`;
    el.appendChild(row); total += it.price*it.qty;
  });
  document.getElementById('cart-total').innerText = total.toFixed(2);
  Array.from(document.querySelectorAll('#cart-contents input[type=number]')).forEach(inp=>{
    inp.addEventListener('change', async e=>{
      const id = parseInt(e.target.dataset.id);
      const qty = parseInt(e.target.value);
      const resp = await fetch('/api/cart/', { method:'PUT', headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')}, body: JSON.stringify({ action:'update', item:{id:id, qty:qty} }) });
      const d = await resp.json(); renderCart(d.cart);
    });
  });
  Array.from(document.querySelectorAll('.remove-btn')).forEach(btn=>{
    btn.addEventListener('click', async e=>{
      const id = parseInt(e.target.dataset.id);
      const resp = await fetch('/api/cart/', { method:'DELETE', headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')}, body: JSON.stringify({ action:'remove', item:{id:id} }) });
      const d = await resp.json(); renderCart(d.cart);
    });
  });
}
document.getElementById('place-order').addEventListener('click', async ()=>{
  if(!confirm('Place order? (no payment)')) return;
  const resp = await fetch('/api/order/', { method:'POST', headers:{'X-CSRFToken': getCookie('csrftoken')} });
  const data = await resp.json();
  if(data.error) alert('Order failed: ' + data.error);
  else alert('Order placed! ID: ' + data.order_id + '\nTotal: ' + data.total);
  await loadCart();
});
async function loadCart(){ const r = await fetch('/api/cart/'); const d = await r.json(); renderCart(d.cart); }
document.getElementById('chat-send').addEventListener('click', async ()=>{
  const inp = document.getElementById('chat-input');
  const msg = inp.value.trim(); if(!msg) return;
  appendChat('You: ' + msg); inp.value='';
  try{
    const resp = await fetch('/api/chat/',{ method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')}, body: JSON.stringify({ message: msg }) });
    const data = await resp.json();
    if(data.reply) appendChat('Bot: ' + data.reply);
    else appendChat('Bot error: ' + (data.error||JSON.stringify(data)));
  }catch(e){
    appendChat('Bot error: ' + e.toString());
  }
});
function appendChat(text){ const log = document.getElementById('chat-log'); const p = document.createElement('div'); p.innerText = text; log.appendChild(p); log.scrollTop = log.scrollHeight; }
function getCookie(name){ let v = document.cookie.match('(^|;)\s*'+name+'\s*=\s*([^;]+)'); return v ? v.pop() : ''; }
fetchMenu(); loadCart();
