[**vite-project v0.0.0**](../../../README.md)

***

# Type Alias: UserProfile

> **UserProfile** = `object`

Defined in: [src/models/Types.ts:23](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L23)

Represents a registered user in the system.

## Properties

### email

> **email**: `string`

Defined in: [src/models/Types.ts:25](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L25)

User’s email address (must be unique).

***

### username

> **username**: `string`

Defined in: [src/models/Types.ts:24](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L24)

Unique identifier chosen by the user.

***

### verified

> **verified**: `boolean` \| `null`

Defined in: [src/models/Types.ts:26](https://github.com/GiannisKat123/AILA-application/blob/main/frontend/src/models/Types.ts#L26)

Whether the email is verified.
- `true` → user’s email is verified
- `false` → verification pending or failed
- `null` → verification status unknown (e.g., session expired)
