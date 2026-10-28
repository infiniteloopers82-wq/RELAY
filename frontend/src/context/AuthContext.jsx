import {createContext,useContext,useEffect,useState} from 'react';
import {api} from '../api/client';
const Auth=createContext(null);
export function AuthProvider({children}){const [user,setUser]=useState(null);const [loading,setLoading]=useState(true);useEffect(()=>{api.me().then(r=>setUser(r.user)).catch(()=>setUser(null)).finally(()=>setLoading(false))},[]);return <Auth.Provider value={{user,setUser,loading}}>{children}</Auth.Provider>}
export const useAuth=()=>useContext(Auth);
