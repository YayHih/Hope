
<template>
<a onclick="history.back()" class="previous">&#8249;</a>
<!-- check later, but will have to change this to sex dpeending how they veiw it -->
<button class="home">Hope</button>
<div class = "logingender">

 
  <p>What is your gender?</p>
  <div class="button-holder">
    <router-link to="/age" class="button" @click="continue2('f')"><img src="female.png">Female</router-link>
    <router-link to="/age" class="button" @click="continue2('m')"><img src="male.png">Male</router-link>
    <router-link to="/age" class="button" @click="continue2('o')"><img src="other_gender.png">Other</router-link>
  </div>
</div>
</template>

<script>
export default {
  name: "LoginGender",
  methods: {
    continue2: function (gender){
      console.log(gender);
      document.cookie = `gender=${gender};`;
    }
  }
};

</script>

<style scoped>
 
  
</style>
