<template>
<button class="home">Hope</button>
  <div @load="user()">
    <!-- <img alt="Faith logo" src="../assets/logo.png">--->
    <p>
      Hope is a way to effortlessly check the availablity of shelters,
      soup kitchens, volenteer opportunities and more. 
    </p>
    <p>
      We will collect a few pieces of information to help best get you started.
          </p>
    
    <router-link to="/language" class="continue">Continue <img src="continue.png"></router-link>  
    <!-- try to chose something that isnt an image for the continue button -->
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
window.onload = function() {
    // similar behavior as clicking on a link
    if (window.location.href=='http://localhost:8080/'&&this.getcookies()>0){
      //https://stackoverflow.com/questions/5968196/how-do-i-check-if-a-cookie-exists
      console.log("here");
    window.location.href = "http://stackoverflow.com";
    }
}
export default {
  name: 'First',
  components: {
    HelloWorld
  },
  // methods: {
  //   user:function (){
  //     console.log("home");
  //    user += getCookie(children);
  //    if (user !=""){
  //     console.log("next");
  //    }
    
  // }
  // // },
  // created:function (){
  //   this.user()
  // }
}
</script>
<style scoped>

</style>
