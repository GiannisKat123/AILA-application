export type UserProfile = {
    username: string;
    email: string;
}

export type Message = {
    message: string;
    timestamp: string;
    role:string
}

export type LoginAPIOutput = {
    user_details: UserProfile;
}
