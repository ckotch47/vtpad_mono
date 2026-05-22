<template>
  <tr v-if="item.id !== undefined">
    <td class="short-name">{{ item.short_name }}
      <br>
      <a v-if="item.external_link"
         :href="item.external_link ?? '#'"
         target="_blank">{{item.external_link ? item.external_link.split('/').pop() : ''}}
      </a>
    </td>
    <td class="title" @click="$emit('openBug')">{{ item.title }}</td>
    <td class="text-no-wrap username-no-wrap " :class="settings.compact ? 'text-center username-compact' : ''" >
      <v-avatar
        color="grey"
        size="24"
        v-if="item.assigner_id"
      >
        <span class="text-h5" v-if="!item.assigner_user?.avatar.filepath">{{item.assigner_user?.username ? item.assigner_user?.username[0]?.toUpperCase() : '@'}}</span>
        <v-img :src="item.assigner_user?.avatar.filepath" v-else/>
      </v-avatar>
      {{!settings.compact ? item.assigner_user?.username ?? '' : ''}}
    </td>
    <td :class="`color-state--${item.state.toUpperCase()}`">{{item.state}}</td>
    <td class="tag-chip">
        <custom-chip-component
          v-for="tag in item.tag.slice(0, settings.compact ? 3 : 4)"
          :key="tag.id"
          :color="tag.color"
          :text="tag.title"
          @click="$emit('ClickTagEmit', tag.id)"
          />
    </td>
    <td class="text-no-wrap username-no-wrap " :class="settings.compact ? 'text-center username-compact' : ''">
      {{item.create_user?.avatar_filepath}}
      <v-avatar
        color="grey"
        size="24"
        v-if="item.create_user_id"
      >
        <span class="text-h5" v-if="!item.create_user?.avatar.filepath">{{item.create_user?.username ? item.create_user?.username[0]?.toUpperCase() : '@'}}</span>
        <v-img :src="item.create_user?.avatar.filepath" v-else/>
      </v-avatar>
      {{!settings.compact ? item.create_user.username ?? '' : ''}}
    </td>

    <td class="text-no-wrap"  v-if="!settings.compact">{{item.estimate_date ? item.estimate_date.split('T')[0] : ''}}</td>
  </tr>
</template>

<script>
import CustomChipComponent from "@/components/common/chips/customChipComponent.vue";

export default {
  name: "bugsListRowComponent",
  components: {CustomChipComponent},
  emits: ['ClickTagEmit', 'openBug'],
  props: {
    item: Object,
    settings: Object
  }
}
</script>

<style lang="scss">

</style>
