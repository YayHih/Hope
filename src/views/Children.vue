<template>
<a onclick="history.back()" class="previous">&#8249;</a>
<button class="home">Hope</button>
  <div class="children">
    <p>Do you have any children (18 and under).</p>
    <div class="button-holder">
      <router-link to="/home" class="button" @click="children('0')"><img src="person.png">No&nbsp;children</router-link>
      <router-link to="/home" class="button" @click="children('1')"><img src="person_1.png">One&nbsp;child</router-link>
      <router-link to="/home" class="button" @click="children('2')"><img src="person_2.png">Two&nbsp;or&nbsp;more&nbsp;children</router-link>
      <router-link to="/home" class="button" @click="children('na')"><img src="na.png">I'd&nbsp;prefer&nbsp;not&nbsp;to&nbsp;say</router-link>
    </div>
  </div>
  
</template>
<script>

export default {
  name: "Children",
  methods: {
    children: function (amountStr) {
      console.log(amountStr);
      document.cookie = `chidren=${amountStr};`;
    }
  }
}
</script>
<style scoped>
  
</style>