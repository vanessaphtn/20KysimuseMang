<template>
  <div class="container">
    <GameComponent
      :question="question"
      :words="words"
      :loading="loading"
      :gameOver="gameOver"
      :finalWord="finalWord"
      :endMessage="endMessage"
      @answer="handleAnswer"
      @undo="undoLastAnswer"
      @game-over="gameOver = true"
      @final-answer="handleFinalAnswer"
    />

    <div v-if="history.length > 0" class="history">
      <h3>Vastused:</h3>
      <div v-for="(entry, index) in history" :key="index" class="history-item">
        {{ index + 1 }}. {{ entry.question }} → <strong>
          <span v-if="entry.answer === 1">Jah</span>
        <span v-else-if="entry.answer === 0">Ei</span>
        <span v-else-if="entry.answer === 3">Ei</span>
        <span v-else-if="entry.answer === 4">Peaaegu</span>
        <span v-else>Ei tea</span></strong>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import GameComponent from "@/Components/GameComponent.vue";

export default {
  components: {
    GameComponent,
  },
  data() {
    return {
      question: "",
      loading: true,
      words: [],
      category: "",
      history: [],
      gameOver: false,
      finalWord: "",
      endMessage: "",
    };
  },
  async mounted() {
    this.category = this.$route.params.category;
    await this.loadWords();
  },
  methods: {
    async loadWords() {
  try {
    const response = await axios.get(`/api/words/${this.category}`);
    this.words = response.data;

    if (this.words.length > 0) { // Kontrollime, kas massiiv ei ole tühi
      if (await this.startGame()) {
        console.log("olen siin")
        await this.getQuestion();
      }
      console.log("ei lähe sisse")
    }
  } catch (error) {
    console.error("Sõnade laadimine ebaõnnestus:", error);
  }
},
async startGame() {
  try {
    const response = await axios.get("/api/start");
    if (response.status === 200) {
      // Tagastame true, kui mäng alustati edukalt
      return true;
    }
  } catch (error) {
    console.error("Mängu alustamine ebaõnnestus:", error);
  }
  // Tagastame false, kui midagi läks valesti
  return false;
},

    async getQuestion() {
      try {
        this.loading = true;  // Määrame laadimise olekuks true
        const response = await axios.get("/api/question");
        this.loading = false;  // Lõpetame laadimise

        if (response.data.word) {
          this.finalWord = response.data.word;
          this.gameOver = true;
        } else {
          this.question = response.data.question;
        }
      } catch (error) {
        console.error("Küsimuse laadimine ebaõnnestus:", error);
      }
    },

    async handleAnswer(userAnswer) {
      try {
        this.loading = true;  // Määrame laadimise olekuks true
        const response = await axios.post("/api/answer", { answer: userAnswer });

        await this.fetchHistory();


        if (response.data.word) {
          this.finalWord = response.data.word;
          await this.handleFinalAnswer();
          this.gameOver = true;
        } else {
          this.question = response.data.question;
        }

        this.loading = false;  // Lõpetame laadimise
      } catch (error) {
        console.error("Vastuse saatmine ebaõnnestus:", error);
        this.loading = false;
      }
    },

    async fetchHistory() {
      try {
        const response = await axios.get("/api/history");

        this.history = response.data.questions.map((question, index) => ({
          question: question,
          answer: response.data.answers[index]
        }));

      } catch (error) {
        console.error("Ajaloo laadimine ebaõnnestus:", error);
      }
    },

    async undoLastAnswer() {
      try {
      const response = await axios.post('/api/undo');

      // Kui päring õnnestub, värskendame ajalugu ja küsimust
      if (response.data.message) {
        console.log(response.data.message); 
        this.question = response.data.question;
        await this.fetchHistory(); 
      }
    } catch (error) {
      console.error('Viimase küsimuse tagasivõtmine ebaõnnestus:', error);
    }
  },
    async handleFinalAnswer(finalAnswer) {
      try {
        const response = await axios.post("/api/end", { answer: finalAnswer });
        await this.fetchHistory();
        if (response.data.outcome) {
          console.log(response.data.outcome)
          this.endMessage = response.data.outcome;
          this.gameOver = true;
        } else if (response.data.continue) {
          await this.getQuestion();
          this.gameOver = false;
        }
      }
      catch (error) {
        console.error("Lõpetamine ebaõnnestus:", error);
      }


  },
  },
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

.history{
  font-family: "Tiny5", serif;
  font-weight: 400;
  font-style: normal;
  color: #ffe7bd;
  text-shadow: 4px 4px 0px black;

}
</style>
