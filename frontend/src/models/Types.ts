/**
 * ============================================================
 * Type Definitions – Core Data Models
 * ============================================================
 * These types define the data contracts used across the frontend.
 * They ensure strong typing when interacting with the backend API.
 *
 * Each type corresponds to a resource or response structure
 * exchanged between frontend and backend.
 */

/**
 * UserProfile
 * -----------
 * Represents a registered user in the system.
 *
 * Fields:
 * - username: string → unique identifier chosen by the user.
 * - email: string → user’s email address (must be unique).
 * - verified: boolean | null → whether the email is verified.
 *   - true → user’s email is verified
 *   - false → verification pending or failed
 *   - null → verification status unknown (e.g., session expired or incomplete)
 */
export type UserProfile = {
  username: string;
  email: string;
  verified: boolean | null;
};

/**
 * Message
 * -------
 * Represents a chat message inside a conversation.
 *
 * Fields:
 * - feedback: boolean | null → user’s feedback on assistant’s reply.
 *   - true → positive feedback
 *   - false → negative feedback
 *   - null → no feedback given
 * - id: string → unique identifier (UUID).
 * - message: string → message text.
 * - timestamp: string → ISO-8601 formatted timestamp.
 * - role: string → sender role ("user" | "assistant").
 */
export type Message = {
  feedback: boolean | null;
  id: string;
  message: string;
  timestamp: string;
  role: string;
};

/**
 * LoginAPIOutput
 * --------------
 * Returned by the login API when authentication succeeds.
 *
 * Fields:
 * - user_details: UserProfile → the authenticated user’s profile info.
 */
export type LoginAPIOutput = {
  user_details: UserProfile;
};

/**
 * Conversations
 * -------------
 * Represents a conversation/chat thread.
 *
 * Fields:
 * - conversation_name: string → display name/title of the conversation.
 * - conversation_id: string → unique identifier (UUID).
 */
export type Conversations = {
  conversation_name: string;
  conversation_id: string;
};

/**
 * ErrorMessage
 * ------------
 * Represents an error object returned by API calls.
 *
 * Fields:
 * - error_message: string → descriptive error message from backend.
 */
export type ErrorMessage = {
  error_message: string;
};
