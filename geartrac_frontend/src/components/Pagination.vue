<script setup>
const props = defineProps({
  totalItems: {
    type: Number,
    required: true,
  },
  itemsPerPage: {
    type: Number,
    default: 10,
  },
  currentPage: {
    type: Number,
    default: 1,
  },
  next: {
    type: String,
    default: null,
  },
  previous: {
    type: String,
    default: null,
  },
});

const emit = defineEmits(["update:currentPage", "updatePage"]);

function changePage(n) {
  emit("update:currentPage", n);
  emit("updatePage");
}
</script>

<template>
  <div class="join">
    <button
      class="join-item btn"
      :disabled="!previous"
      @click="changePage(currentPage - 1)"
    >
      Previous
    </button>

    <button class="join-item btn btn-primary">
      {{ currentPage }}
    </button>

    <button class="join-item btn" :disabled="!next" @click="changePage(currentPage + 1)">
      Next
    </button>
  </div>
</template>
