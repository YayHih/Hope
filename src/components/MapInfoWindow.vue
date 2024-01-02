<template>
	<div>
		<slot></slot>
	</div>
</template>

<script>
	export default {
		props: {
			lat: { type: Number, required: true },
			lng: { type: Number, required: true }
		},
		data: () => ({
			infoW: null
		}),
		mounted() {
			this.$parent.getMap(map => {
				(this.infoW = new window.google.maps.InfoWindow({
					position: { lat: this.lat, lng: this.lng },
					content: this.$el,
					disableAutoPan: true
				})),
					this.infoW.open(map)
			})
		},
		beforeDestroy() {
			this.infoW.close()
		}
	}
</script>