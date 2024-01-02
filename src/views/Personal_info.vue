<template >
<a onclick="history.back()" class="previous">&#8249;</a>
  <div  class="maincon">
    <p >
      To optimize your experience, we collect a few points of information including:
    </p>
    <p>
      What langauge you speak, <br />
      What gender you are, <br />
      How old you are, <br />
      And how many children you have.
    </p>
    <br />
    <br />
    <p>The information we recieved from you are:</p>
    <p id="demo">a</p>
  </div>
</template>
<script>
export default {
  name: "Personal_info",
  methods: {
    getCookies: function () {
      let ca = decodeURIComponent(document.cookie).split(";");
      let allValues = "";
      for (let i = 0; i < ca.length; i++) {
        allValues += ca[i] + "\n";
      }
      return allValues;
    },
    checkCookies: function () {
        document.getElementById("demo").innerHTML = this.getCookies();
    },
  },
  mounted() {
    this.checkCookies()
  },
};
</script>
<style scoped>

</style>