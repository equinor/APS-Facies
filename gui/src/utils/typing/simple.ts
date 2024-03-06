export type Optional<T> = T | null
export type Maybe<T> = Optional<T> | undefined

export type OptionalKey<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

declare const __brand: unique symbol
type Brand<B> = { [__brand]: B }
export type Branded<K, T> = K & Brand<T>
