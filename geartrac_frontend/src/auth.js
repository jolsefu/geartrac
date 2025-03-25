import axios from 'axios'
import { googleSdkLoaded } from 'vue3-google-login'
import google_keys from '../../google_keys.json'

/**
 *
 * CSRF AND HTTP-ONLY COOKIE TOKEN AUTHENTICATION
 *
 */

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

/**
 *
 * AUTHENTICATION FUNCTIONS
 *
 */

export async function authLogIn() {
  await api.get('auth/csrf/');

  googleSdkLoaded((google) => {
    google.accounts.oauth2
      .initCodeClient({

        client_id: google_keys.web.client_id,
        scope: 'email profile',
        redirect_uri: 'http://localhost:8000/api/v1/auth/google/callback/',
        callback: (response) => {
          if (response.code) { sendCodeToBackend(response.code); }
        },

      })
      .requestCode();
  });
};

export async function authLogOut() {
  try {

    const response = await api.post('auth/logout/');

    console.log(response.data);

    window.location.href = 'login';

  } catch (error) {

    console.error("Failed to log out:", error);

  }
}

async function sendCodeToBackend(code) {
  try {

    const response = await api.post('auth/google/', {'code': code});

    console.log(response);

  } catch (error) {

    console.error('Failed to send authorization code:', error);

  }
};

export function authTest() {
  try {

    const response = api.get('auth/protected/')

    console.log(response);

  } catch (error) {

    console.error('Failed to authenticate', error);

  }
}
