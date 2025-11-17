import axios, {type AxiosInstance} from 'axios';

function createApi(): AxiosInstance{
    return axios.create({
        // baseURL: 'https://ailademo.fly.dev', // ✅ Production deployment
        baseURL: 'http://localhost:8080', // ✅ Local development
        // baseURL: '/', // ✅ Default: relative path (frontend proxy)
        // baseURL: 'http://ailabot.upatras.gr',
        withCredentials:true
    })
}

export const api: AxiosInstance = createApi()
export default api
export {createApi}
export type {AxiosInstance}