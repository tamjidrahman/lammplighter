import FileUpload from './FileUpload';
import MyTable from './Table';

import React from 'react';
import { Container, Grid, Typography } from '@mui/material';
import NewRunForm from './NewRunForm';

const App: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Lammplighter
      </Typography>

      <Grid container justifyContent="flex-end" alignItems="center">
        <FileUpload />
      </Grid>
      <NewRunForm />

      <MyTable />

      {/* You can add more components or content as needed */}
    </Container>
  );
};

export default App;
