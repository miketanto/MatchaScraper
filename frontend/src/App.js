import React, { useState } from 'react';
import axios from 'axios';
import { Button, TextField, CircularProgress, Box, Modal, Typography } from '@mui/material';
import SpotifyAuth from './SpotifyAuth';
import './index.css';

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [currentToken, setCurrentToken] = useState({
    access_token: null,
    refresh_token: null,
    expires_in: null,
    expires: null,
  });

  const handleSubmit = async () => {
    setIsLoading(true);
    const spotifyToken = currentToken.access_token;
    try {
      const response = await axios.post(process.env.REACT_APP_API_URL, {
        spotifyToken,
        youtubeUrl,
      });
      setResponseMessage(response.data.message);
    } catch (error) {
      console.error('Error uploading to YouTube:', error);
      setResponseMessage('Failed to upload to YouTube.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseModal = () => {
    setResponseMessage('');
  };

  return (
    <Box
      sx={{
        backgroundColor: 'black',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'gray',
        padding: 2,
      }}
    >
      <SpotifyAuth currentToken={currentToken} setCurrentToken={setCurrentToken} />
      
      <Typography
        variant="h2"
        sx={{
          color: 'white',
          textAlign: 'center',
          fontWeight: 500,
          marginBottom: 4,
        }}
      >
        <span style={{ color: 'red' }}>YouTube</span> 2{' '}
        <span style={{ color: 'green' }}>Spotify</span>
      </Typography>
      {currentToken.access_token?
      <Box
      sx={{
        width: '100%',
        maxWidth: '400px',
        bgcolor: 'black',
        borderRadius: 2,
        padding: 3,
      }}
    >
      <TextField
        label="YouTube URL"
        variant="outlined"
        value={youtubeUrl}
        onChange={(e) => setYoutubeUrl(e.target.value)}
        fullWidth
        InputLabelProps={{
          style: { color: 'gray' },
        }}
        InputProps={{
          style: { color: 'gray', borderColor: 'gray' },
        }}
        sx={{
          marginBottom: 2,
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'gray',
            },
            '&:hover fieldset': {
              borderColor: 'gray',
            },
            '&.Mui-focused fieldset': {
              borderColor: 'spotifyGreen',
            },
          },
        }}
      />
      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={isLoading}
        fullWidth
        sx={{
          bgcolor: 'green',
          color: 'white',
          '&:hover': {
            bgcolor: 'darkgreen',
          },
        }}
      >
        Submit
      </Button>
    </Box>
      :null
    }
      <Modal
        open={isLoading || !!responseMessage}
        onClose={handleCloseModal}
        aria-labelledby="loading-modal-title"
        aria-describedby="loading-modal-description"
      >
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 400,
            bgcolor: 'black',
            border: '2px solid gray',
            boxShadow: 24,
            p: 4,
            textAlign: 'center',
            color: 'white',
          }}
        >
          {isLoading ? (
            <CircularProgress sx={{ color: 'gray' }} />
          ) : (
            <Typography id="loading-modal-description">
              {responseMessage}
            </Typography>
          )}
          {!isLoading && (
            <Button onClick={handleCloseModal} variant="contained" color="primary" sx={{ mt: 2, bgcolor: 'green' }}>
              Close
            </Button>
          )}
        </Box>
      </Modal>
      <Box sx={{ position:'absolute', bottom: '0vh', textAlign: 'center', padding: '10px 0' }}>
        <Typography variant="body2" sx={{ color: 'gray' }}>
          Powered by Langchain
        </Typography>
      </Box>
    </Box>
  );
};

export default App;
