<template>

      <v-expansion-panels class="expansion-custom">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between flex-grow-1">
            {{this.comment.create_user.username}} change {{this.textJson.name}}
              <div class="flex-shrink-0">
                {{this.comment.create_date ? this.comment.create_date.split('T')[0] : ''}}
              </div>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <s v-html="sanitizedFrom"></s> <span v-html="sanitizedTo"/>
          </v-expansion-panel-text>

        </v-expansion-panel>
      </v-expansion-panels>


</template>

<script>
import { sanitizeHtml } from '@/utils/sanitize';

export default {
  name: "bugsModalCommentHistoryElem",
  props:{
    username: String,
    text: String,
    date: String,
    comment: Object
  },
  data(){
    return{
      textJson: {
        name: undefined,
        from: undefined,
        to: undefined
      }
    }
  },
  computed: {
    sanitizedFrom() {
      return sanitizeHtml(this.textJson?.from);
    },
    sanitizedTo() {
      return sanitizeHtml(this.textJson?.to);
    }
  },
  mounted() {
    try {
      this.textJson = JSON.parse(this.comment.text)
    }catch (e) {
      this.textJson= {
        name: undefined,
          from: undefined,
          to: undefined
      }
    }
  }
}
</script>

<style lang="scss">
.expansion-custom{
  .v-expansion-panel {
    &__shadow{
      box-shadow: none;
    }
    &-title {
      padding: 0;
      min-height: unset;
      border: none;
      &--active{
        min-height: unset !important;
      }
      &:hover{
        background-color: unset;
      }
      &__icon {
        display: none;
      }
    }
  }
}
</style>
