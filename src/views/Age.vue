<template>
<a onclick="history.back()" class="previous">&#8249;</a>
<button class="home">Hope</button>
  <div class="age">
    <p>Please enter your age range.</p>
    <div class="button-holder">
      <router-link to="/children" class="button" @click="age('18')"><img src="child.png">Below&nbsp;18</router-link>
      <router-link to="/children" class="button" @click="age('18-65')"><img src="adult.png">18&nbsp;through&nbsp;65</router-link>
      <router-link to="/children" class="button" @click="age('65')"><img src="elderly.png">65&nbsp;years&nbsp;or&nbsp;older</router-link>
      <router-link to="/children" class="button" @click="age('na')"><img src="na.png">I'd&nbsp;prefer&nbsp;not&nbsp;to&nbsp;say</router-link>
      <!-- have these be customised to the gender later on -->
      
    </div>
  </div>
  
</template>
<script>

export default {
  name: "Age",
  methods: {
    age: function (amountStr) {
      console.log(amountStr);
      document.cookie = `age=${amountStr};`;
    }
  }
}
</script>
<style scoped>
</style>