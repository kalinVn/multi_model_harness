# TennisBallSlider

## Additional Description and Functionality

Build `TennisBallSlider` from its persistent Feature Component specification and declared design and Vue prototypes.

The component renders only the decorative WebGL tennis ball. Training renders the shared Start Training Button below it and owns camera or training initialization, pending state, authorization, and navigation.

The default prototype footprint is 216 by 216 pixels with no container background, border, or shadow. On Training, the page places the slider in the former heading position, keeps the Training heading and introductory sentence directly to its right, and aligns the Start Training action below the ball. The right-hand Coaching Cue, Connection, and Session stack remains independently aligned with the LIVE COACHING eyebrow. Those page-layout decisions do not belong to the slider controller.

`TennisBallSlider.vue` follows the Home Page Video Slider lifecycle structure: it owns DOM refs and mount/unmount integration, creates one controller, calls `init()` and `play()` after mount, and calls `destroy()` before unmount. `TennisBallSliderController` owns WebGL resources, the render loop, resize observation, and public `play()`, `stop()`, and `destroy()` methods.

The controller uses the seamless repository asset `prototypes/design/assets/tennis-ball-felt-texture.png` as the surface texture on a permanently round WebGL sphere. The rendered surface adds two thin off-white curved seams near the upper and lower edges, soft directional highlights and edge shading for depth, and two identical dark `PLAY` labels with a fuzzy felt treatment. The labels occupy opposite sides of the texture so a second `PLAY` enters view as the first disappears behind the sphere.

The sphere stays fixed on the right while its felt, seams, and labels rotate horizontally together; the sphere itself must never flatten. Lighting must keep the ball predominantly bright tennis green with only localized darker areas, and no visible geometry grid or detached overlay may appear. It must not bounce, move forward and backward, travel vertically, render a court background, or load a decorative player photograph. The sphere is hidden from assistive technology and stops animating when reduced motion is requested.

## References

- `docs/frontend/feature-components.md#tennisballslider`
- `prototypes/design/components/sliders/tennis-ball-slider.html`
- `prototypes/pages/TrainingPage.vue`
- `prototypes/components/sliders/tennis-ball-slider/TennisBallSlider.vue`
- `prototypes/components/sliders/tennis-ball-slider/TennisBallSliderController.js`
