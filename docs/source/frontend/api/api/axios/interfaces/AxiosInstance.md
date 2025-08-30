[**vite-project v0.0.0**](../../../README.md)

***

# Interface: AxiosInstance()

Defined in: [node\_modules/axios/index.d.ts:513](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L513)

## Extends

- `Axios`

## Call Signature

> **AxiosInstance**\<`T`, `R`, `D`\>(`config`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:514](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L514)

### Type Parameters

#### T

`T` = `any`

#### R

`R` = `AxiosResponse`\<`T`, `any`\>

#### D

`D` = `any`

### Parameters

#### config

`AxiosRequestConfig`\<`D`\>

### Returns

`Promise`\<`R`\>

## Call Signature

> **AxiosInstance**\<`T`, `R`, `D`\>(`url`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:515](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L515)

### Type Parameters

#### T

`T` = `any`

#### R

`R` = `AxiosResponse`\<`T`, `any`\>

#### D

`D` = `any`

### Parameters

#### url

`string`

#### config?

`AxiosRequestConfig`\<`D`\>

### Returns

`Promise`\<`R`\>

## Properties

### defaults

> **defaults**: `Omit`\<`AxiosDefaults`\<`any`\>, `"headers"`\> & `object`

Defined in: [node\_modules/axios/index.d.ts:518](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L518)

#### Type Declaration

##### headers

> **headers**: `HeadersDefaults` & `object`

#### Overrides

`Axios.defaults`

***

### interceptors

> **interceptors**: `object`

Defined in: [node\_modules/axios/index.d.ts:495](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L495)

#### request

> **request**: `AxiosInterceptorManager`\<`InternalAxiosRequestConfig`\<`any`\>\>

#### response

> **response**: `AxiosInterceptorManager`\<`AxiosResponse`\<`any`, `any`\>\>

#### Inherited from

`Axios.interceptors`

## Methods

### create()

> **create**(`config?`): `AxiosInstance`

Defined in: [node\_modules/axios/index.d.ts:517](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L517)

#### Parameters

##### config?

`CreateAxiosDefaults`\<`any`\>

#### Returns

`AxiosInstance`

***

### delete()

> **delete**\<`T`, `R`, `D`\>(`url`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:502](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L502)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.delete`

***

### get()

> **get**\<`T`, `R`, `D`\>(`url`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:501](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L501)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.get`

***

### getUri()

> **getUri**(`config?`): `string`

Defined in: [node\_modules/axios/index.d.ts:499](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L499)

#### Parameters

##### config?

`AxiosRequestConfig`\<`any`\>

#### Returns

`string`

#### Inherited from

`Axios.getUri`

***

### head()

> **head**\<`T`, `R`, `D`\>(`url`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:503](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L503)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.head`

***

### options()

> **options**\<`T`, `R`, `D`\>(`url`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:504](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L504)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.options`

***

### patch()

> **patch**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:507](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L507)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.patch`

***

### patchForm()

> **patchForm**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:510](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L510)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.patchForm`

***

### post()

> **post**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:505](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L505)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.post`

***

### postForm()

> **postForm**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:508](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L508)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.postForm`

***

### put()

> **put**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:506](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L506)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.put`

***

### putForm()

> **putForm**\<`T`, `R`, `D`\>(`url`, `data?`, `config?`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:509](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L509)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### url

`string`

##### data?

`D`

##### config?

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.putForm`

***

### request()

> **request**\<`T`, `R`, `D`\>(`config`): `Promise`\<`R`\>

Defined in: [node\_modules/axios/index.d.ts:500](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/node_modules/axios/index.d.ts#L500)

#### Type Parameters

##### T

`T` = `any`

##### R

`R` = `AxiosResponse`\<`T`, `any`\>

##### D

`D` = `any`

#### Parameters

##### config

`AxiosRequestConfig`\<`D`\>

#### Returns

`Promise`\<`R`\>

#### Inherited from

`Axios.request`
