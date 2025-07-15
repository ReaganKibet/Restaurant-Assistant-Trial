import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";

interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  image?: string;
  dietary_tags?: string[];
  ingredients?: string[];
  allergens?: string[];
  cuisine_type?: string;
  [key: string]: any;
}

interface MenuSectionProps {
  preferences: any;
}

export const MenuSection: React.FC<MenuSectionProps> = ({ preferences }) => {
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [selectedMeal, setSelectedMeal] = useState<MenuItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch("/api/meals/menu")
      .then(res => res.json())
      .then(data => {
        // If the response is { menu: [...] }, use data.menu; if it's just [...], use data
        if (Array.isArray(data)) {
          setMenu(data);
        } else if (Array.isArray(data.menu)) {
          setMenu(data.menu);
        } else {
          setMenu([]);
        }
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch menu");
        setLoading(false);
      });
  }, []);

  const matchesPreferences = (meal: MenuItem) => {
    // Example: highlight if cuisine or dietary tag matches
    if (!preferences) return false;
    if (
      preferences.favorite_cuisines?.includes(meal.cuisine_type) ||
      meal.dietary_tags?.some((tag: string) => preferences.dietary_restrictions?.includes(tag))
    ) {
      return true;
    }
    return false;
  };

  return (
    <Box sx={{ mt: 3, padding: 4 }}>
      <Typography variant="h4" gutterBottom>Our Menu</Typography>
      {loading && <Typography>Loading menu...</Typography>}
      {error && <Typography color="error">{error}</Typography>}
      <Grid container spacing={3}>
        {menu.map(meal => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={meal.id}>
            <Card
              sx={{ height: '100%', display: 'flex', flexDirection: 'column', boxShadow: 3 }}
              onClick={() => setSelectedMeal(meal)}
            >
              {meal.image && (
                <CardMedia
                  component="img"
                  height="160"
                  image={meal.image}
                  alt={meal.name}
                />
              )}
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="div" gutterBottom>
                  {meal.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {meal.description}
                </Typography>
                <Typography variant="subtitle2" color="primary">
                  Cuisine: {meal.cuisine_type}
                </Typography>
                <Typography variant="subtitle2">
                  Price: ${meal.price}
                </Typography>
                <Typography variant="subtitle2">
                  Spice Level: {selectedMeal?.spice_level ?? "N/A"}
                </Typography>
                <Typography variant="subtitle2">
                  Dietary: {(selectedMeal?.dietary_tags && selectedMeal.dietary_tags.length > 0)
                    ? selectedMeal.dietary_tags.join(", ")
                    : "None"}
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {/* Cuisine type chip */}
                  {meal.cuisine_type && (
                    <Chip label={meal.cuisine_type} size="small" color="info" />
                  )}
                  {/* Dietary tags chips */}
                  {Array.isArray(meal.dietary_tags) && meal.dietary_tags.map((tag: string) => (
                    <Chip key={tag} label={tag} size="small" color="success" />
                  ))}
                </Box>
              </CardContent>
              <Button
                variant="contained"
                color="primary"
                sx={{ m: 2 }}
                onClick={() => setSelectedMeal(meal)}
              >
                Order Now
              </Button>
            </Card>
          </Grid>
        ))}
      </Grid>
      {/* Meal Details Dialog */}
      <Dialog open={!!selectedMeal} onClose={() => setSelectedMeal(null)} maxWidth="sm" fullWidth>
        {selectedMeal && (
          <>
            <DialogTitle>{selectedMeal.name}</DialogTitle>
            <DialogContent>
              {selectedMeal.image && (
                <Box sx={{ mb: 2 }}>
                  <img src={selectedMeal.image} alt={selectedMeal.name} style={{ width: '100%', borderRadius: 8 }} />
                </Box>
              )}
              <Typography variant="subtitle1">{selectedMeal.description}</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>Price: ${selectedMeal.price}</Typography>
              <Typography variant="body2">Category: {selectedMeal.category || "N/A"}</Typography>
              <Typography variant="body2">
                Cuisine: {selectedMeal.cuisine_type ? selectedMeal.cuisine_type : "N/A"}
              </Typography>
              <Typography variant="body2">Spice Level: {selectedMeal.spice_level ?? "N/A"}</Typography>
              <Typography variant="body2">
                Dietary: {(selectedMeal.dietary_tags && selectedMeal.dietary_tags.length > 0)
                  ? selectedMeal.dietary_tags.join(", ")
                  : "None"}
              </Typography>
              <Typography variant="body2">
                Allergens: {(selectedMeal.allergens && selectedMeal.allergens.length > 0)
                  ? selectedMeal.allergens.join(", ")
                  : "None"}
              </Typography>
              <Typography variant="body2">
                Ingredients: {(selectedMeal.ingredients && selectedMeal.ingredients.length > 0)
                  ? selectedMeal.ingredients.join(", ")
                  : "N/A"}
              </Typography>
              <Typography variant="body2">
                Vegetarian: {selectedMeal.is_vegetarian ? "Yes" : "No"}
              </Typography>
              <Typography variant="body2">
                Vegan: {selectedMeal.is_vegan ? "Yes" : "No"}
              </Typography>
              <Typography variant="body2">
                Gluten Free: {selectedMeal.is_gluten_free ? "Yes" : "No"}
              </Typography>
              <Typography variant="body2">
                Dairy Free: {selectedMeal.is_dairy_free ? "Yes" : "No"}
              </Typography>
              {selectedMeal.nutritional_info && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">
                    Nutrition: {`Calories: ${selectedMeal.nutritional_info.calories}, Protein: ${selectedMeal.nutritional_info.protein}g, Carbs: ${selectedMeal.nutritional_info.carbs}g, Fat: ${selectedMeal.nutritional_info.fat}g`}
                  </Typography>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedMeal(null)}>Close</Button>
              <Button variant="contained" color="primary">Add to Order</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};