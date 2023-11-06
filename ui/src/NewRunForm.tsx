import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Button,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    TextField,
    Typography,
    Box,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface InputConfig {
    id: number;
    name: string;
    s3_path: string;
    // Add more fields as needed
}

const instance = axios.create({ baseURL: process.env.REACT_APP_API_URL });

const NewRunForm: React.FC = () => {
    const [inputConfigs, setInputConfigs] = useState<InputConfig[]>([]);
    const [selectedInputConfig, setSelectedInputConfig] = useState<string>('');
    const [commands, setCommands] = useState<string[]>(['']);

    useEffect(() => {
        // Fetch inputconfigs from your API
        instance
            .get<InputConfig[]>('resources/inputs/')
            .then((response) => {
                setInputConfigs(response.data);
            })
            .catch((error) => {
                console.error('Error fetching inputconfigs:', error);
            });
    }, []);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Create a new run with the selected inputconfig and commands
        instance
            .post('execute', {
                input_id: selectedInputConfig,
                commands: commands,
            })
            .then((response) => {
                console.log('New run created:', response.data);
                // You can perform additional actions after successful submission
            })
            .catch((error) => {
                console.error('Error creating a new run:', error);
            });
    };

    const handleAddCommand = () => {
        if (commands.length < 5) {
            setCommands([...commands, '']); // Add an empty command field
        }
    };

    const handleRemoveCommand = (index: number) => {
        const updatedCommands = [...commands];
        updatedCommands.splice(index, 1); // Remove the command at the specified index
        setCommands(updatedCommands);
    };

    const handleCommandChange = (index: number, value: string) => {
        const updatedCommands = [...commands];
        updatedCommands[index] = value; // Update the command at the specified index
        setCommands(updatedCommands);
    };

    return (
        <div
            style={{
                padding: '20px',
                border: '1px solid #e0e0e0',
                borderRadius: '5px',
            }}
        >
            <Typography variant="h5" style={{ marginBottom: '20px' }}>
                Create a New Run
            </Typography>
            <form onSubmit={handleFormSubmit}>
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                        <Box
                            border={1}
                            borderRadius="5px"
                            p={2}
                            style={{ marginBottom: '20px' }}
                        >
                            <Typography variant="h6">Choose Input</Typography>
                            <FormControl fullWidth>
                                <InputLabel>Select Input</InputLabel>
                                <Select
                                    value={selectedInputConfig}
                                    onChange={(e) => setSelectedInputConfig(e.target.value as string)}
                                    label="Package Type"
                                >
                                    <MenuItem value="">
                                        <em>Select an Input Config</em>
                                    </MenuItem>
                                    {inputConfigs.map((inputConfig) => (
                                        <MenuItem
                                            key={inputConfig.id}
                                            value={inputConfig.id.toString()}
                                        >
                                            {inputConfig.name}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Box border={1} borderRadius="5px" p={2}>
                            <Typography variant="h6">Add Commands</Typography>
                            {commands.map((command, index) => (
                                <Grid item xs={12} key={index}>
                                    <Box
                                        border={1}
                                        borderRadius="5px"
                                        p={2}
                                        style={{ marginBottom: '20px' }}
                                    >
                                        <FormControl fullWidth>
                                            <TextField
                                                label={`Command ${index + 1}`}
                                                fullWidth
                                                value={command}
                                                onChange={(e) => handleCommandChange(index, e.target.value)}
                                            />
                                            <Button
                                                type="button"
                                                onClick={() => handleRemoveCommand(index)}
                                            >
                                                Remove
                                            </Button>
                                        </FormControl>
                                    </Box>
                                </Grid>
                            ))}
                            <Grid item xs={12}>
                                <Button
                                    type="button"
                                    onClick={handleAddCommand}
                                    startIcon={<AddIcon />}
                                >
                                    Add Command
                                </Button>
                            </Grid>
                        </Box>
                    </Grid>
                </Grid>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    style={{ float: 'left', marginTop: '20px' }}
                >
                    Submit
                </Button>
            </form>
        </div>
    );
};

export default NewRunForm;
