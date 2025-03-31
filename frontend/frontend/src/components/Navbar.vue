<template>
    <div>
      <RouterLink to="/"><h1>20 KÜSIMUSE MÄNG</h1></RouterLink>
     
      <div class="info-circle" @mouseover="showInfo" @mouseleave="hideInfo">
        <span class="circle-text">?</span>
        <div v-if="show" class="info-tooltip">
          <p> Mängujuhis: </p>
            <p>> Alustamiseks vali sobiv mängu kategooria. </p>
            <p>> Seejärel vali endale meelepärane sõna.</p>
            <p>> Vastates küsimustele, juhindu oma valitud sõnast.</p>
            <p>> Kui mõni küsimus on segane või ei oska vastata, vajuta "Ei tea" nuppu.</p>
            <p>> Arvutil on maksimaalselt 20 küsimust, et ära arvata sinu valitud sõna.</p>
            <p>> Kui pakutud sõna on lähedal, aga mitte päris õige vajuta "Peaaegu" nuppu.</p>
            <p> Head mängu! :)</p>
        </div>
      </div>
    </div>
  </template>

<script setup>
import { ref } from 'vue';

const show = ref(false);

const showInfo = () => {
  show.value = true;
};

const hideInfo = () => {
  show.value = false;
};
</script>


<style scoped>

h1 {
font-family: "Tiny5", serif;
  font-style:normal;
  font-weight: bolder;
  font-size: 50px;
  color: #ffe7bd;
  text-shadow: 4px 4px 0px black;
  text-decoration: none; 
  
  display: inline-block;
}
.router-link-active,
.router-link-exact-active {
  text-decoration: none; 
}

.info-circle {
  position: fixed;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  background-color: #3c2b61;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: "Tiny5", serif;
  font-size: 20px;
  color: black;
  cursor: pointer;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
  border: 4px solid black;
}

.info-circle:hover{
  color: #ffe7bd;
  background-color: #925BB3;
  border: 4px solid #ffe7bd;
}
.circle-text {
  text-align: center;
}

.info-tooltip {
  position: fixed; 
  top: 50%; 
  left: 50%; 
  transform: translate(-50%, -50%); 
  background-color: rgba(0, 0, 0, 0.9); 
  color: #ffe7bd;
  padding: 20px;
  border-radius: 8px;
  width: 80%; 
  max-width: 500px; 
  text-align: center;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
}

.info-circle:hover .info-tooltip {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 600px) {
  h1 {
    font-size: 30px;
  }
}
</style>