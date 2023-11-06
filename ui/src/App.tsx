import FileUpload from './FileUpload';
import MyTable from './Table';

import { Container, Grid, Typography } from '@mui/material';
import NewRunForm from './NewRunForm';

import {
  ClerkProvider,
  SignedIn,
  SignedOut,
  RedirectToSignIn,
  UserButton
} from "@clerk/clerk-react";

if (!process.env.REACT_APP_CLERK_PUBLISHABLE_KEY) {
  throw "Missing Publishable Key"
}

const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <SignedIn>

        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom>
            Lammplighter
          </Typography>

          <UserButton />

          <Grid container justifyContent="flex-end" alignItems="center">
            <FileUpload />
          </Grid>
          <NewRunForm />

          <MyTable />

          {/* You can add more components or content as needed */}
        </Container>
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </ClerkProvider>
  );
}

export default App;