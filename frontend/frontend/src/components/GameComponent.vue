<template>
    <div>
      <div class="word-selection-group">
        <h3>Valitud sõna: </h3>
        <select v-if="words.length > 0" v-model="selectedWord" class="word-selection" :class="{'selected': selectedWord}">
          <option value="" disabled>Muuda</option>
          <option v-for="word in words" :key="word" :value="word">
            {{ word}}
          </option>
        </select>
      </div>
  
      <!-- Küsimus -->
      <p v-if="selectedWord && loading && !gameOver" class="question">Laen küsimust...</p>
      <p v-else-if="selectedWord && !loading && !gameOver" class="question">{{ question }}</p>
  
      <!-- Vastuse nupud -->
      <div class="button-group" v-if="selectedWord && !loading && !gameOver">
        <button v-if="question" @click="answer('jah')" class="retro-button">Jah</button>
        <button v-if="question" @click="answer('ei')" class="retro-button">Ei</button>
        <button v-if="question" @click="answer('ei tea')" class="retro-button">Ei tea</button>
        <button v-if="question" @click="undo()" class="retro-button">Tagasi</button>
      </div>
  
    <!-- Kui pakub lõppsõna -->
    <div v-if="showFinalGuess">
      <p class="question">Kas sõna oli {{ finalWord }}?</p>
      <button @click="handleFinalGuess('jah')" class="retro-button">Jah</button>
      <button @click="handleFinalGuess('peaaegu')" class="retro-button">Oled lähedal</button>
      <button @click="handleFinalGuess('ei')" class="retro-button">Ei</button>
    </div>

    <!-- Kui mäng lõpeb -->
    <div v-if="gameOver">
      <p class="question">{{ endMessage }}</p>
      <RouterLink to="/" v-if="endMessage"><button class="retro-button">Alusta uuesti</button></RouterLink>
    </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      question: String,
      words: Array,
      loading: Boolean,
      gameOver: Boolean,
      finalWord: String,
      endMessage: String,
    },
    data() {
      return {
        selectedWord: "",
        showFinalGuess: false,
      };
    }, watch: {
  gameOver(newVal) {
    if (newVal && this.finalWord) {
      this.showFinalGuess = true;
    }
  }
},
    methods: {
      answer(userAnswer) {
        this.$emit("answer", userAnswer);
      },
      undo() {
        this.$emit("undo");
      },
      restartGame() {
        this.$emit("restart");
      },
      handleFinalGuess(finalAnswer) {
        this.$emit("final-answer", finalAnswer);
        this.showFinalGuess = false;
       }
    },
  };
  </script>
  
<style scoped>

h3{
  font-family: "Tiny5", serif;
  font-weight: 400;
  font-style: normal;
  color: #ffe7bd;
  text-shadow: 4px 4px 0px black;
}

.question {
  /*font-family: "Tiny5", serif;*/
  font-family: "Jersey 10", sans-serif;
  font-size: 40px;
  color: #ffe7bd;
  text-shadow: 4px 4px 0px black;
}

.word-selection-group{
  margin-top: 10px;
  display: flex;
  justify-content: center; 
  flex-wrap: wrap; 
  gap: 20px; 
}

.word-selection{
  font-family: "Tiny5", serif;
  background-color: #3c2b61;
  border: 4px solid black;
  color: black;
  padding: 12px 24px;
  font-size: 25px;
  cursor: pointer;
  box-shadow: 4px 4px 0px black;
  transition: all 0.1s ease-in-out;
  min-width: 150px; 
  border-radius: 8px;

}

.word-selection.selected {
  color: #ffe7bd;
  background-color: #925BB3;
  border: 4px solid #ffe7bd;
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

@media (max-width: 600px) {
  .button-group {
    flex-direction: column; 
  }

  .retro-button {
    width: 100%; 
    font-size: 16px; /* smaller on small screens */
  }

  .question {
    font-size: 24px; /* adjust question size */
  }

  .word-selection {
    font-size: 18px; /* adjust word button size */
    padding: 10px 20px;
    min-width: 120px;
  }

  h3 {
    font-size: 20px;
  }
}


</style>
  