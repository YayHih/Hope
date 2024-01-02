<template>
  <a onclick="history.back()" class="previous">&#8249;</a>
  <div class="maincon">
    <!-- Choose a starting location either manually or by pressing
      <button @click="location()" id="location_button">Your Location</button> -->
    <div id="list1" class="dropdown-check-list" tabindex="100">
      <span class="anchor">Filter</span>
      <ul class="items" id="inputs" @input="this.get_val" >
        <li>Shelters<input type="checkbox" id="shelterc"  name="shelterc" value="shelterc" /></li>
        <li>Foodbanks<input type="checkbox" id="foodbankc" value="foodbankc"  /></li>
        <li>dropin<input type="checkbox" id="dropinc" value="dropinc" /></li>
      </ul>
    </div>
  </div>

  <div id="map" ref="map">
    <map-info-window :lat="40.736780" :lng="-73.952110"><img src="house.png" id="house" /></map-info-window>
    <!--Assessment Center Greenpoint, Brooklyn-->
    <map-info-window :lat="40.803420" :lng="-73.937900"><img src="house.png" id="house" /></map-info-window>
    <!--Boulevard Residence East Harlem, Manhattan-->
    <map-info-window :lat="40.744860" :lng="-73.992980"><img src="house.png" id="house" /> </map-info-window>
    <!--Ryan Residence (Chelsea, Manhattan)-->
    <map-info-window :lat="40.732450" :lng="-73.989270"><img src="house.png" id="house" /></map-info-window>
    <!--Palace Employment Residence (the Bowery, Manhattan)-->
    <map-info-window :lat="40.862620" :lng="-73.911280"><img src="house.png" id="house" /></map-info-window>
    <!--Reaching New Heights Residence (Fordham, Bronx)-->
    <map-info-window :lat="40.728250" :lng="-73.991400"><img src="house.png" id="house" /></map-info-window>
    <!--Homes for the Homeless-->
    <map-info-window :lat="40.883780" :lng="-73.878660"><img src="house.png" id="house" /></map-info-window>
    <!--The Bowery Mission -Tribeca Campus-->
    <map-info-window :lat="40.916560" :lng="-73.795060"><img src="house.png" id="house" /></map-info-window>
    <!--Volunteers of America - Crossroads-->
    <map-info-window :lat="40.745200" :lng="-73.981480"><img src="house.png" id="house" /></map-info-window>
    <!--Grand Central Neighborhood Social Services Corporation (GCNSSC)-->
    <map-info-window :lat="40.749960" :lng="-73.991430"><img src="house.png" id="house" /></map-info-window>
    <!--Bailey House Inc.-->
    <map-info-window :lat="40.725120" :lng="-73.991980"><img src="dropin.png" id="dropin" /></map-info-window>
    <!--BRC Project Rescue Drop-In Center-->
    <map-info-window :lat="40.757400" :lng="-73.963870"><img src="dropin.png" id="dropin" /></map-info-window>
    <!--Catholic Charities of The Archdiocese of New York--->
    <map-info-window :lat="40.688320" :lng="-73.983830"><img src="dropin.png" id="dropin" /></map-info-window>
    <!--Bond St. Drop-In Center-->
    <map-info-window :lat="40.749360" :lng="-73.998980"><img src="foodbank.png" id="foodbank" /></map-info-window>
    <!--Holy Apostles Soup Kitchen-->

    <!-- <map-info-window :lat="-23.344" :lng="129.036">
      <span style="background: red">Test 2</span>
    </map-info-window> -->

  </div>
  <!-- https://stackoverflow.com/questions/50650815/vue-add-a-component-on-button-click/50651082 -->
  <!-- https://xon5.medium.com/vue-google-maps-c16da293c71 -->
</template>

<script>
import MapMarker from "../components/MapMarker";
import MapInfoWindow from "../components/MapInfoWindow";
import ShelterMapM18 from "../components/ShelterMapM18";

export default {

  name: 'Mapping',
  components: {
    MapMarker,
    MapInfoWindow,

  },
  data: () => ({
    map: null,
  }),
  //   var: myloc = new google.maps.Marker({
  //     clickable: false,
  //     icon: new google.maps.MarkerImage('//maps.gstatic.com/mapfiles/mobile/mobileimgs2.png',
  //                                                     new google.maps.Size(22,22),
  //                                                     new google.maps.Point(0,18),
  //                                                     new google.maps.Point(11,11)),
  //     shadow: null,
  //     zIndex: 999,
  //     map: "map"
  // }),
  methods: {
    get_val: function () {
      const parent = document.getElementById("map");
      const foodbank = document.getElementById("fb");
      let foodbankbl = true;
      let dropinbl = true;
      let shelterbl = true;
      const shelterc = document.querySelector('#shelterc');
      console.log(shelterc.checked)
      //https://www.javascripttutorial.net/javascript-dom/javascript-checkbox/#:~:text=Checking%20if%20a%20checkbox%20is%20checked&text=First%2C%20select%20the%20checkbox%20using,%3B%20otherwise%2C%20it%20is%20not.
    },
    location: function () {
      navigator.geolocation.getCurrentPosition((position) => {
        this.center = {

          lat: position.coords.latitude,
          lng: position.coords.longitude,
          new: google.maps.Marker({
            position: (this.lat, this.lng),

            // https://developers.google.com/maps/documentation/javascript/markers
            //https://github.com/xon52/medium-tutorial-vue-maps-example
            //https://stackoverflow.com/questions/9142833/show-my-location-on-google-maps-api-v3
            //https://developers.google.com/maps/documentation/javascript/markers

            //https://medium.com/@glavecoding/google-map-api-in-vue-js-925c7052a9b6 
          }),
        };
      });
    },
    getMap(callback) {
      let vm = this;
      function checkForMap() {
        if (vm.map) callback(vm.map);
        else setTimeout(checkForMap, 200);
      }
      checkForMap();
    },
  },
  mounted() {
    this.map = new window.google.maps.Map(this.$refs["map"], {
      center: { lat: 40.749364, lng: -73.999159 },
      zoom: 10,
    });
    var checkList = document.getElementById('list1');
    checkList.getElementsByClassName('anchor')[0].onclick = function (evt) {

      if (checkList.classList.contains('visible'))
        checkList.classList.remove('visible');
      else
        checkList.classList.add('visible');
    }

  },
};

</script>
<map-marker :lat=x :lng=y></map-marker>
<style scoped>
#house,
#dropin,
#foodbank {
  height: 4em;
  width: 4em;
}

#map {
  top: 10rem;
  height: 600px;
}

:root {
  x: 41.75;
  y: 73.999159;
}

.dropdown-check-list {
  display: inline-block;
}

.dropdown-check-list {
  background: white;
}

.dropdown-check-list .anchor {
  position: relative;
  cursor: pointer;
  display: inline-block;
  padding: 5px 50px 5px 10px;
  /* border: 1px solid #ccc; */
}

.dropdown-check-list .anchor:after {
  position: absolute;
  content: "";
  border-left: 2px solid black;
  border-top: 2px solid black;
  padding: 5px;
  right: 10px;
  top: 20%;
  -moz-transform: rotate(-135deg);
  -ms-transform: rotate(-135deg);
  -o-transform: rotate(-135deg);
  -webkit-transform: rotate(-135deg);
  transform: rotate(-135deg);
}

.dropdown-check-list .anchor:active:after {
  right: 8px;
  top: 21%;
}

.dropdown-check-list ul.items {
  padding: 2px;
  display: none;
  margin: 0;
  border: 1px solid #ccc;
  border-top: none;
}

.dropdown-check-list ul.items li {
  list-style: none;
}

.dropdown-check-list.visible .anchor {
  color: #0094ff;
}

.dropdown-check-list.visible .items {
  display: block;
}
</style>