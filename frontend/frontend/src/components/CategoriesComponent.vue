<template>
  <div class="container">
    <h2>VALI MÄNGU KATEGOORIA JA RASKUSASTE:</h2>
    <h2>Lihtne → LOOMAD & VILJAD</h2>
    <h2>Keskmine → LOOMAD, SÖÖDAVAD VILJAD </h2>
    <h2> Keeruline → MINERAALID</h2>

    <div class="button-group">
      <button @click="goToGame('easy')" class="retro-button">Loomad & Viljad</button>
      <button @click="goToGame('animals')" class="retro-button">Loomad</button>
      <button @click="goToGame('plants')" class="retro-button">Söödavad viljad</button>
      <button @click="goToGame('minerals')" class="retro-button">Mineraalid</button>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    goToGame(category) {
      this.$router.push(`/game/${category}`);
    }
  }
};
</script>


<style scoped>
.container {
  text-align: center;  /* Center everything */
  background:rgb(80, 23, 74);
  max-width: 50%; 
  margin: 20px auto;
  padding: 40px;

  border-radius: 15px;
  box-shadow: 4px 4px 0px black;
}

h2 {
  font-family: "Tiny5", serif;
  font-weight: 400;
  font-style: normal;
  color: #ffe7bd;
  text-shadow: 4px 4px 0px black;
}

/* Flexbox for buttons */
.button-group {
  margin-top: 80px;
  display: flex;
  justify-content: center; 
  flex-wrap: wrap; 
  gap: 20px; 
}

/* Make buttons responsive */
.retro-button {
  font-family: "Tiny5", serif;
  background-color: #925BB3;
  border: 4px solid black;
  color: #ffe7bd;
  padding: 12px 24px;
  font-size: 20px;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: 4px 4px 0px black;
  transition: all 0.1s ease-in-out;
  min-width: 150px; 
  border-radius: 8px;
}

/* Button click effect */
.retro-button:active {
  box-shadow: 2px 2px 0px black;
  transform: translate(2px, 2px);
}
.retro-button:hover{
  color: #ffe7bd;
  background-color: #925BB3;
  border: 4px solid #ffe7bd;
  box-shadow: 7px 7px 0px black;
}

/* Responsive design */
@media (max-width: 600px) {
  .button-group {
    flex-direction: column; 
  }

  .retro-button {
    width: 100%; 
  }
}


</style>