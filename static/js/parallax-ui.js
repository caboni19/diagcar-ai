(function(){
  const starsContainer=document.getElementById('stars');
  if(starsContainer && !starsContainer.dataset.ready){
    starsContainer.dataset.ready='1';
    for(let i=0;i<100;i++){const s=document.createElement('div');s.className='star';s.style.left=Math.random()*100+'%';s.style.top=Math.random()*100+'%';s.style.animationDelay=Math.random()*3+'s';s.style.animationDuration=(Math.random()*3+2)+'s';starsContainer.appendChild(s)}
  }
  const follower=document.getElementById('mouseFollower');
  if(follower){let mx=0,my=0,fx=0,fy=0;document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});function loop(){fx+=(mx-fx)*.12;fy+=(my-fy)*.12;follower.style.left=fx+'px';follower.style.top=fy+'px';requestAnimationFrame(loop)}loop()}
  document.querySelectorAll('.hero-card,.card,.quick-grid button,.form-card,.vehicle-panel,.chat-panel').forEach(el=>{
    el.addEventListener('mousemove',e=>{const r=el.getBoundingClientRect();const x=e.clientX-r.left;const y=e.clientY-r.top;const rx=(y-r.height/2)/35;const ry=(r.width/2-x)/35;el.style.transform=`perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-3px)`});
    el.addEventListener('mouseleave',()=>{el.style.transform=''})
  });
})();
