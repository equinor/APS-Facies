import type { Validation } from '@vuelidate/core'
import type {
  InjectionKey,
  Ref,
} from 'vue'
import {
  inject,
  onBeforeUnmount,
  onMounted,
  provide,
  reactive,
} from 'vue'

const invalidationKey = Symbol(
  'Key for invalidation provide/inject.',
) as InjectionKey<{
  on: (vuelidate: Ref<Validation>) => void
  off: (vuelidate: Ref<Validation>) => void
}>

export function useInvalidation(vuelidate: Ref<Validation>) {
  const invalidationContext = inject(invalidationKey, {
    on: () => {},
    off: () => {},
  })

  onMounted(() => invalidationContext?.on(vuelidate))
  onBeforeUnmount(() => invalidationContext?.off(vuelidate))
}

export function provideInvalidation() {
  const vuelidateRefs = reactive<Set<Ref<Validation>>>(new Set())

  function on(vuelidate: Ref<Validation>) {
    vuelidateRefs.add(vuelidate)
  }
  function off(vuelidate: Ref<Validation>) {
    vuelidateRefs.delete(vuelidate)
  }
  provide(invalidationKey, { on, off })

  function invalidate() {
    for (const vuelidateRef of vuelidateRefs) {
      vuelidateRef.value.$touch()
    }
  }

  return { invalidate }
}
