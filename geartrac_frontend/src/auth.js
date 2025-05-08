import axios from 'axios'
import { ref, reactive } from 'vue'

import { googleSdkLoaded } from 'vue3-google-login'
import google_keys from '../../google_keys.json'

/**
 *
 * CSRF AND HTTP-ONLY COOKIE TOKEN AUTHENTICATION
 *
 */

const auth = axios.create({
  baseURL: 'http://localhost:8000/auth/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export const authNotify = reactive({
  messageTitle: "",
  message: "",
});


export const isAuthenticated = ref(false)
export const userDetails = ref({})
export const userPermissionLevel = ref(0)

export const checkAuth = async () => {
  try {
    const response = await auth.get('validate/')
    isAuthenticated.value = response.status === 200
  } catch (error) {
    isAuthenticated.value = false
  }

  return isAuthenticated.value
}

const retrieveDetails = async () => {
  try {
    const response = await auth.get('details/')
    userDetails.value = response.data
  } catch (error) {
    userDetails.value = null
  }
}

const retrievePermissionLevel = async () => {
  try {
    const response = await auth.get('permission/')
    userPermissionLevel.value = response.data.level
  } catch (error) {
    userPermissionLevel.value = 0
  }
}

checkAuth()
retrieveDetails()
retrievePermissionLevel()

/**
 *
 * AUTHENTICATION FUNCTIONS
 *
 */

export async function authLogIn() {
  await auth.get('csrf/')

  googleSdkLoaded((google) => {
    google.accounts.oauth2
      .initCodeClient({
        client_id: google_keys.web.client_id,
        scope: 'email profile',
        redirect_uri: 'http://localhost:8000/api/v1/auth/google/callback/',
        callback: (response) => {
          if (response.code) {
            sendCodeToBackend(response.code)
          }
        },
      })
      .requestCode()
  })
}

export async function authLogOut() {
  try {
    const response = await auth.post('logout/')

    window.location.href = 'login'
  } catch (error) {
    authNotify.message = error.response.data.error;
    authNotify.messageTitle = error.response.status === 200 ? "Success" : "Error";
    authNotify.error = true;
  }
}

async function sendCodeToBackend(code) {
  try {
    const response = await auth.post('google/', { code: code })

    window.location.href = '/'
  } catch (error) {
    authNotify.message = error.response.data.error[0];
    authNotify.messageTitle = error.response.status === 200 ? "Success" : "Error";
    authNotify.error = true;
  }
}

export function authTest() {
  try {
    const response = auth.get('validate/')

    console.log(response)
  } catch (error) {
    console.error('Failed to authenticate', error)
  }
}
