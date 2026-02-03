/**
 * HUNTIQ V3 - useCart Hook
 * Hook for shopping cart management
 */

import { useState, useEffect, useCallback } from 'react';
import { CartService } from '@/services';
import { toast } from 'sonner';

export const useCart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [cartCount, setCartCount] = useState(0);
  const [cartTotal, setCartTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch cart items
  const fetchCart = useCallback(async () => {
    setLoading(true);
    try {
      const items = await CartService.getItems();
      setCartItems(items);
      
      // Calculate count and total
      const count = items.reduce((sum, item) => sum + (item.quantity || 1), 0);
      const total = items.reduce((sum, item) => sum + (item.price * (item.quantity || 1)), 0);
      
      setCartCount(count);
      setCartTotal(total);
      
      return items;
    } catch (err) {
      // Cart might be empty, not an error
      setCartItems([]);
      setCartCount(0);
      setCartTotal(0);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Add item to cart
  const addToCart = useCallback(async (product, quantity = 1) => {
    try {
      await CartService.addItem({
        product_id: product.id,
        quantity,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
      });
      
      await fetchCart();
      toast.success(`${product.name} ajouté au panier`);
      return true;
    } catch (err) {
      setError(err.message);
      toast.error('Erreur lors de l\'ajout au panier');
      return false;
    }
  }, [fetchCart]);

  // Update item quantity
  const updateQuantity = useCallback(async (itemId, quantity) => {
    if (quantity < 1) {
      return removeItem(itemId);
    }
    
    try {
      await CartService.updateQuantity(itemId, quantity);
      await fetchCart();
      return true;
    } catch (err) {
      setError(err.message);
      toast.error('Erreur lors de la mise à jour');
      return false;
    }
  }, [fetchCart]);

  // Remove item from cart
  const removeItem = useCallback(async (itemId) => {
    try {
      await CartService.removeItem(itemId);
      await fetchCart();
      toast.success('Article retiré du panier');
      return true;
    } catch (err) {
      setError(err.message);
      toast.error('Erreur lors de la suppression');
      return false;
    }
  }, [fetchCart]);

  // Clear cart
  const clearCart = useCallback(async () => {
    try {
      await CartService.clearCart();
      setCartItems([]);
      setCartCount(0);
      setCartTotal(0);
      toast.success('Panier vidé');
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  return {
    cartItems,
    cartCount,
    cartTotal,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    fetchCart,
    sessionId: CartService.getSessionId(),
  };
};

export default useCart;
