<template>
  <tr v-if="item.id !== undefined">
    <td class="short-name">
      {{ item.short_name }}
      <br>
      <a v-if="item.external_link" :href="item.external_link ?? '#'" target="_blank">
        {{ item.external_link ? item.external_link.split('/').pop() : '' }}
      </a>
    </td>
    <td class="title" @click="$emit('openBug')">{{ item.title }}</td>
    <td class="text-no-wrap username-no-wrap" :class="settings.compact ? 'text-center username-compact' : ''">
      <v-avatar
        v-if="item.assigner_id"
        color="grey"
        size="24"
      >
        <span v-if="!item.assigner_user?.avatar.filepath" class="text-h5">
          {{ item.assigner_user?.username ? item.assigner_user?.username[0]?.toUpperCase() : '@' }}
        </span>
        <v-img v-else :src="item.assigner_user?.avatar.filepath" :alt="item.assigner_user?.username || 'Assignee avatar'" />
      </v-avatar>
      {{ !settings.compact ? item.assigner_user?.username ?? '' : '' }}
    </td>
    <td :class="`color-state--${item.state.toUpperCase()}`">{{ item.state }}</td>
    <td class="tag-chip">
      <custom-chip-component
        v-for="tag in item.tag.slice(0, settings.compact ? 3 : 4)"
        :key="tag.id"
        :color="tag.color"
        :text="tag.title"
        @click="$emit('ClickTagEmit', tag.id)"
      />
    </td>
    <td class="text-no-wrap username-no-wrap" :class="settings.compact ? 'text-center username-compact' : ''">
      {{ item.create_user?.avatar_filepath }}
      <v-avatar
        v-if="item.create_user_id"
        color="grey"
        size="24"
      >
        <span v-if="!item.create_user?.avatar.filepath" class="text-h5">
          {{ item.create_user?.username ? item.create_user?.username[0]?.toUpperCase() : '@' }}
        </span>
        <v-img v-else :src="item.create_user?.avatar.filepath" :alt="item.create_user?.username || 'Creator avatar'" />
      </v-avatar>
      {{ !settings.compact ? item.create_user.username ?? '' : '' }}
    </td>
    <td v-if="!settings.compact" class="text-no-wrap">
      {{ item.estimate_date ? item.estimate_date.split('T')[0] : '' }}
    </td>
  </tr>
</template>

<script setup>
import CustomChipComponent from '@/components/common/chips/customChipComponent.vue'

defineProps({
  item: Object,
  settings: Object
})

defineEmits(['ClickTagEmit', 'openBug'])
</script>

<style lang="scss">
</style>
