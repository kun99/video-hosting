<template>
    <div class="flex flex-col justify-center items-center text-white h-72">
        <h1 class="mb-4 font-bold text-4xl">Success</h1>
        <p >You will be redirected in a few seconds...</p>
    </div>
</template>
    
<script>
export default {
  mounted() {
    setTimeout(() => {
      this.$router.push('/');
    }, 5000);
  },
};
</script>
    