import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Button, Card, CardContent, Typography, Avatar, Box, IconButton, Menu, MenuItem } from '@mui/material';

const clientId = process.env.REACT_APP_SPOTIFY_CLIENT_ID
const redirectUrl = process.env.REACT_APP_SPOTIFY_REDIRECT_URL
const scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private';

const SpotifyAuth = ({ currentToken, setCurrentToken }) => {
  const [userData, setUserData] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const effectExecuted = useRef(false);
  const open = Boolean(anchorEl);

  useEffect(() => {
    // Check if there's a valid access token in localStorage
    const storedToken = {
      access_token: localStorage.getItem('access_token'),
      refresh_token: localStorage.getItem('refresh_token'),
      expires_in: localStorage.getItem('expires_in'),
      expires: localStorage.getItem('expires'),
    };

    if (effectExecuted.current) return; // Prevents the effect from running again
    effectExecuted.current = true;

    if (storedToken.access_token && new Date(storedToken.expires) > new Date()) {
      setCurrentToken(storedToken);
    } else {
      // On page load, try to fetch auth code from current browser search URL
      const args = new URLSearchParams(window.location.search);
      const code = args.get('code');

      // If we find a code, we're in a callback, do a token exchange
      if (code) {
        getToken(code).then((token) => {
          saveToken(token);
          // Remove code from URL so we can refresh correctly.
          const url = new URL(window.location.href);
          url.searchParams.delete('code');
          const updatedUrl = url.search ? url.href : url.href.replace('?', '');
          window.history.replaceState({}, document.title, updatedUrl);
        });
      }
    }
  }, []);

  useEffect(() => {
    if (currentToken.access_token) {
      // If we have a token, we're logged in, so fetch user data and render logged-in template
      getUserData().then((data) => {
        setUserData(data);
      });
    }
  }, [currentToken.access_token]);

  const redirectToSpotifyAuthorize = async () => {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const randomValues = crypto.getRandomValues(new Uint8Array(64));
    const randomString = randomValues.reduce((acc, x) => acc + possible[x % possible.length], '');

    const code_verifier = randomString;
    const data = new TextEncoder().encode(code_verifier);
    const hashed = await crypto.subtle.digest('SHA-256', data);

    const code_challenge_base64 = btoa(String.fromCharCode(...new Uint8Array(hashed)))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');

    localStorage.setItem('code_verifier', code_verifier);

    const authUrl = new URL('https://accounts.spotify.com/authorize');
    const params = {
      response_type: 'code',
      client_id: clientId,
      scope: scope,
      code_challenge_method: 'S256',
      code_challenge: code_challenge_base64,
      redirect_uri: redirectUrl,
    };

    authUrl.search = new URLSearchParams(params).toString();
    window.location.href = authUrl.toString(); // Redirect the user to the authorization server for login
  };

  const getToken = async (code) => {
    const code_verifier = localStorage.getItem('code_verifier');

    const response = await axios.post('https://accounts.spotify.com/api/token', new URLSearchParams({
      client_id: clientId,
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: redirectUrl,
      code_verifier: code_verifier,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  };

  const getUserData = async () => {
    const response = await axios.get('https://api.spotify.com/v1/me', {
      headers: { 'Authorization': `Bearer ${currentToken.access_token}` },
    });

    return response.data;
  };

  const saveToken = (token) => {
    setCurrentToken({
      access_token: token.access_token,
      refresh_token: token.refresh_token,
      expires_in: token.expires_in,
      expires: new Date(Date.now() + token.expires_in * 1000),
    });

    localStorage.setItem('access_token', token.access_token);
    localStorage.setItem('refresh_token', token.refresh_token);
    localStorage.setItem('expires_in', token.expires_in);
    localStorage.setItem('expires', new Date(Date.now() + token.expires_in * 1000).toISOString());
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
   <div>
      {currentToken.access_token && userData ? (
        <Box
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          bgcolor: 'green',
          borderRadius: '50%',
          p: 1,
        }}
        >
        <>
          <IconButton onClick={handleClick} sx={{ p: 0 }}>
            <Avatar alt={userData.display_name} src={userData.images[0]?.url} />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            MenuListProps={{
              'aria-labelledby': 'basic-button',
            }}
          >
            <MenuItem>
              <Typography variant="h6">{userData.display_name}</Typography>
            </MenuItem>
            <MenuItem>{userData.email}</MenuItem>
            <MenuItem>Followers: {userData.followers.total}</MenuItem>
            <MenuItem>Country: {userData.country}</MenuItem>
          </Menu>
        </>
        </Box>
      ) : (
        <Box
  sx={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    position: 'absolute',
    paddingTop: '10vh',
    width: '100%',
    top: 0,
    left: 0,
    bgcolor: 'transparent',
  }}
>
  <Button
    variant="contained"
    onClick={redirectToSpotifyAuthorize}
    sx={{
      bgcolor: 'green',
      color: 'white',
      padding: '10px 20px',
      fontSize: '1.2rem',
    }}
  >
    Login with Spotify
  </Button>
</Box>

      )}
    </div>
  );
};

export default SpotifyAuth;
