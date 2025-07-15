import React from "react";
import { Box, Card, CardContent, Typography, FormControl, InputLabel, Select, MenuItem, OutlinedInput, Chip, Slider, Button, FormHelperText, Divider, Grid, Paper } from "@mui/material";
import RestaurantIcon from '@mui/icons-material/Restaurant';
import LocalDiningIcon from '@mui/icons-material/LocalDining';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

// Helper for multi-select
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: 224,
      width: 250,
    },
  },
};

type PreferencesProps = {
  preferences: any;
  setPreferences: (prefs: any) => void;
  allergiesList: string[];
  ingredientsList: string[];
  cuisinesList: string[];
  mealTypesList: string[];
  dietaryRestrictionsList: string[];
};

export const Preferences: React.FC<PreferencesProps> = ({
  preferences,
  setPreferences,
  allergiesList,
  ingredientsList,
  cuisinesList,
  mealTypesList,
  dietaryRestrictionsList
}) => {
  const handleChange = (field: string, value: any) => {
    setPreferences({ ...preferences, [field]: value });
  };

  const handleMultiSelect = (field: string, value: string) => {
    const arr = preferences[field] || [];
    if (arr.includes(value)) {
      handleChange(field, arr.filter((v: string) => v !== value));
    } else {
      handleChange(field, [...arr, value]);
    }
  };

  return (
    <Card sx={{ mb: 3, background: '#f9f9f9', boxShadow: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>Preferences</Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 6 }}>
            {/* Dietary Restrictions */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="dietary-restrictions-label">Dietary Restrictions</InputLabel>
              <Select
                labelId="dietary-restrictions-label"
                multiple
                value={preferences.dietary_restrictions}
                onChange={e => handleChange("dietary_restrictions", e.target.value)}
                input={<OutlinedInput label="Dietary Restrictions" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value: string) => (
                      <Chip key={value} label={value} color="success" />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {dietaryRestrictionsList.map(r => (
                  <MenuItem key={r} value={r}>{r}</MenuItem>
                ))}
              </Select>
              <FormHelperText>Choose any dietary restrictions you have.</FormHelperText>
            </FormControl>
            
            {/* Allergies */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="allergies-label">Allergies</InputLabel>
              <Select
                labelId="allergies-label"
                multiple
                value={preferences.allergies}
                onChange={e => handleChange("allergies", e.target.value)}
                input={<OutlinedInput label="Allergies" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value: string) => (
                      <Chip key={value} label={value} color="error" />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {allergiesList.map(a => (
                  <MenuItem key={a} value={a}>{a}</MenuItem>
                ))}
              </Select>
              <FormHelperText>Select ingredients you are allergic to.</FormHelperText>
            </FormControl>
            
            {/* Disliked Ingredients */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="disliked-ingredients-label">Disliked Ingredients</InputLabel>
              <Select
                labelId="disliked-ingredients-label"
                multiple
                value={preferences.disliked_ingredients}
                onChange={e => handleChange("disliked_ingredients", e.target.value)}
                input={<OutlinedInput label="Disliked Ingredients" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value: string) => (
                      <Chip key={value} label={value} color="warning" />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {ingredientsList.map(i => (
                  <MenuItem key={i} value={i}>{i}</MenuItem>
                ))}
              </Select>
              <FormHelperText>Pick ingredients you dislike.</FormHelperText>
            </FormControl>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            {/* Price Range */}
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom><AttachMoneyIcon sx={{ mr: 1 }} />Price Range ($)</Typography>
              <Slider
                value={preferences.price_range}
                onChange={(_, val) => handleChange("price_range", val)}
                valueLabelDisplay="auto"
                min={0}
                max={100}
                step={1}
                sx={{ color: 'primary.main' }}
              />
              <FormHelperText>
                Selected: ${preferences.price_range[0]} to ${preferences.price_range[1]}
              </FormHelperText>
            </Box>
            
            {/* Favorite Cuisines */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="cuisines-label">Favorite Cuisines</InputLabel>
              <Select
                labelId="cuisines-label"
                multiple
                value={preferences.favorite_cuisines}
                onChange={e => handleChange("favorite_cuisines", e.target.value)}
                input={<OutlinedInput label="Favorite Cuisines" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value: string) => (
                      <Chip key={value} label={value} icon={<RestaurantIcon />} color="info" />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {cuisinesList.map(c => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
              </Select>
              <FormHelperText>Pick cuisines you enjoy most.</FormHelperText>
            </FormControl>
            
            {/* Spice Preference */}
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom><WhatshotIcon sx={{ mr: 1 }} />Spice Level</Typography>
              <Slider
                value={preferences.spice_preference}
                onChange={(_, val) => handleChange("spice_preference", val)}
                valueLabelDisplay="auto"
                min={0}
                max={5}
                step={1}
                sx={{ color: 'error.main' }}
              />
              <FormHelperText>How spicy do you like your food?</FormHelperText>
            </Box>
            
            {/* Preferred Meal Types */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="meal-types-label">Preferred Meal Types</InputLabel>
              <Select
                labelId="meal-types-label"
                multiple
                value={preferences.preferred_meal_types}
                onChange={e => handleChange("preferred_meal_types", e.target.value)}
                input={<OutlinedInput label="Preferred Meal Types" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value: string) => (
                      <Chip key={value} label={value} icon={<LocalDiningIcon />} color="secondary" />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {mealTypesList.map(m => (
                  <MenuItem key={m} value={m}>{m}</MenuItem>
                ))}
              </Select>
              <FormHelperText>Choose your preferred meal types.</FormHelperText>
            </FormControl>
            
            {/* Dislikes (general) */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="dislikes-label">Dislikes (general)</InputLabel>
              <OutlinedInput
                id="dislikes"
                value={preferences.dislikes.join(", ")}
                onChange={e => handleChange("dislikes", e.target.value.split(",").map((v: string) => v.trim()))}
                label="Dislikes (general)"
              />
              <FormHelperText>List any other dislikes, separated by commas.</FormHelperText>
            </FormControl>
          </Grid>
        </Grid>
        
        <Divider sx={{ mt: 3, mb: 2 }} />
        {/* Summary */}
        <Paper elevation={3} sx={{ p: 2, background: '#e3f2fd' }}>
          <Typography variant="subtitle2" color="primary">Summary:</Typography>
          <Typography variant="body2">
            Dietary: {preferences.dietary_restrictions.join(", ") || "None"} | Allergies: {preferences.allergies.join(", ") || "None"} | Cuisines: {preferences.favorite_cuisines.join(", ") || "None"} | Price: ${preferences.price_range[0]}-${preferences.price_range[1]}
          </Typography>
        </Paper>
      </CardContent>
    </Card>
  );
};