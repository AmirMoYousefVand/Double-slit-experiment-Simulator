/**
 * Thomas Young Simulator — Interactive HTML5/Canvas/SVG Animations Engine
 * Provides 60 FPS 2D wave propagation (SetupSchematicView equivalent), interactive ray tracing,
 * interactive right-triangle path difference visualizer, historical duel simulation, phasor interference,
 * and quantum buildup with Which-Way toggle.
 */

const PhysicsAnimations = (function () {
    let animId = null;
    let animPhase = 0;
    let buildupParticles = [];
    let buildupObserver = false;
    let buildupTimer = null;

    // Interactive inspection point P state for 2D Wave Propagation & Triangle
    let waveTargetY = 0;
    let isDraggingP = false;

    /**
     * Wavelength (380 - 780 nm) to sRGB Hex color mapping (Dan Bruton algorithm)
     */
    function wavelengthToHex(wl) {
        let r = 0, g = 0, b = 0;
        if (wl >= 380 && wl < 440) {
            r = -(wl - 440) / (440 - 380);
            b = 1.0;
        } else if (wl >= 440 && wl < 490) {
            g = (wl - 440) / (490 - 440);
            b = 1.0;
        } else if (wl >= 490 && wl < 510) {
            g = 1.0;
            b = -(wl - 510) / (510 - 490);
        } else if (wl >= 510 && wl < 580) {
            r = (wl - 510) / (580 - 510);
            g = 1.0;
        } else if (wl >= 580 && wl < 645) {
            r = 1.0;
            g = -(wl - 645) / (645 - 580);
        } else if (wl >= 645 && wl <= 780) {
            r = 1.0;
        }

        let factor = 0.0;
        if (wl >= 380 && wl < 420) {
            factor = 0.3 + 0.7 * (wl - 380) / (420 - 380);
        } else if (wl >= 420 && wl <= 700) {
            factor = 1.0;
        } else if (wl > 700 && wl <= 780) {
            factor = 0.3 + 0.7 * (780 - wl) / (780 - 700);
        }

        const gamma = 0.8;
        const R = Math.round(255 * Math.pow(r * factor, gamma));
        const G = Math.round(255 * Math.pow(g * factor, gamma));
        const B = Math.round(255 * Math.pow(b * factor, gamma));

        return {
            hex: `#${((1 << 24) + (R << 16) + (G << 8) + B).toString(16).slice(1)}`,
            r: R, g: G, b: B
        };
    }

    /**
     * 1. Full 2D Wave Propagation Engine (Matching SetupSchematicView)
     * Features: Laser emitter box, planar waves, barrier with slits (d),
     * expanding Huygens wavelets with alpha falloff, interactive draggable Point P,
     * rays r1 and r2, Delta r right triangle, pulsating impact spot, and physical interference ribbon.
     */
    function startHuygensAnimation(canvas, opts = {}) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const wlNm = opts.wavelength_nm || 632.8;
        const dMm = opts.slit_distance_mm || 0.25;
        const aMm = opts.slit_width_mm || 0.04;
        const lM = opts.screen_distance_m || 1.0;
        const color = wavelengthToHex(wlNm);

        function getCanvasCoords(e) {
            const rect = canvas.getBoundingClientRect();
            return {
                x: (e.clientX - rect.left) * (canvas.width / rect.width),
                y: (e.clientY - rect.top) * (canvas.height / rect.height)
            };
        }

        canvas.onpointerdown = (e) => {
            const pos = getCanvasCoords(e);
            const sx = canvas.width - 55;
            if (pos.x > sx - 80) {
                isDraggingP = true;
                waveTargetY = pos.y - canvas.height / 2;
                canvas.setPointerCapture(e.pointerId);
            }
        };

        canvas.onpointermove = (e) => {
            const pos = getCanvasCoords(e);
            const sx = canvas.width - 55;
            if (pos.x > sx - 80) {
                canvas.style.cursor = 'ns-resize';
            } else {
                canvas.style.cursor = 'default';
            }
            if (isDraggingP) {
                waveTargetY = Math.max(-canvas.height / 2 + 25, Math.min(canvas.height / 2 - 25, pos.y - canvas.height / 2));
            }
        };

        canvas.onpointerup = canvas.onpointercancel = (e) => {
            isDraggingP = false;
            try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
        };

        function loop() {
            const w = canvas.width = canvas.clientWidth || 800;
            const h = canvas.height = canvas.clientHeight || 380;
            const cy = h / 2;
            const xSource = 55;
            const xBarrier = Math.floor(w * 0.36);
            const xScreen = w - 85;

            const slitGap = Math.max(24, Math.min(dMm * 180, h * 0.42));
            const s1 = { x: xBarrier, y: cy - slitGap / 2 };
            const s2 = { x: xBarrier, y: cy + slitGap / 2 };

            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            // 1. Laser Emitter Box
            ctx.fillStyle = '#1E293B';
            ctx.strokeStyle = color.hex;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(14, cy - 24, xSource - 14, 48, 6);
            ctx.fill();
            ctx.stroke();

            // Collimator lens
            ctx.fillStyle = color.hex;
            ctx.beginPath();
            ctx.roundRect(xSource - 4, cy - 14, 6, 28, 2);
            ctx.fill();

            // Planar incident waves marching to barrier
            const numPlanes = 5;
            const planeStep = (xBarrier - xSource) / numPlanes;
            for (let i = 0; i < numPlanes; i++) {
                const px = xSource + ((i * planeStep + animPhase * 14) % (xBarrier - xSource));
                ctx.strokeStyle = color.hex;
                ctx.lineWidth = 1.5;
                ctx.setLineDash([4, 3]);
                ctx.beginPath();
                ctx.moveTo(px, cy - 45);
                ctx.lineTo(px, cy + 45);
                ctx.stroke();
            }
            ctx.setLineDash([]);

            // 2. Double Slit Barrier Plate
            ctx.fillStyle = '#334155';
            ctx.strokeStyle = '#64748B';
            ctx.lineWidth = 1;

            ctx.fillRect(xBarrier - 6, 16, 12, s1.y - 16);
            ctx.strokeRect(xBarrier - 6, 16, 12, s1.y - 16);

            ctx.fillRect(xBarrier - 6, s1.y + 6, 12, s2.y - s1.y - 12);
            ctx.strokeRect(xBarrier - 6, s1.y + 6, 12, s2.y - s1.y - 12);

            ctx.fillRect(xBarrier - 6, s2.y + 6, 12, h - s2.y - 22);
            ctx.strokeRect(xBarrier - 6, s2.y + 6, 12, h - s2.y - 22);

            // Slit nodes S1, S2 and dimension d bracket
            ctx.fillStyle = '#00E676';
            ctx.beginPath();
            ctx.arc(s1.x, s1.y, 4, 0, Math.PI * 2);
            ctx.arc(s2.x, s2.y, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = '#F59E0B';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(xBarrier - 16, s1.y);
            ctx.lineTo(xBarrier - 16, s2.y);
            ctx.stroke();

            ctx.fillStyle = '#F59E0B';
            ctx.font = 'bold 11px Space Grotesk, sans-serif';
            ctx.fillText(`d=${dMm.toFixed(2)}mm`, xBarrier - 56, cy + 4);

            // 3. Expanding Huygens Circular Wavelets with realistic distance falloff
            const maxR = w * 0.62;
            for (let r = 18; r < maxR; r += 26) {
                const rr = r + 6 * Math.sin(animPhase);
                if (rr <= 4) continue;
                const alpha = Math.max(0.12, 1.0 - rr / maxR);

                ctx.strokeStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha * 0.8})`;
                ctx.lineWidth = 1.6;
                ctx.beginPath();
                ctx.arc(s1.x, s1.y, rr, -Math.PI * 0.42, Math.PI * 0.42);
                ctx.stroke();

                ctx.strokeStyle = `rgba(245, 158, 11, ${alpha * 0.7})`;
                ctx.beginPath();
                ctx.arc(s2.x, s2.y, rr, -Math.PI * 0.42, Math.PI * 0.42);
                ctx.stroke();
            }

            // 4. Physical Interference Ribbon on Screen
            const screenTop = 20;
            const screenBottom = h - 20;
            ctx.fillStyle = '#0F172A';
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 2;
            ctx.fillRect(xScreen - 6, screenTop, 12, screenBottom - screenTop);
            ctx.strokeRect(xScreen - 6, screenTop, 12, screenBottom - screenTop);

            const dM = dMm * 1e-3;
            const aM = aMm * 1e-3;
            const wlM = wlNm * 1e-9;
            const scaleYPerPixel = (wlM * lM) / (dM * 18.0);

            for (let pyIdx = screenTop; pyIdx < screenBottom; pyIdx += 2) {
                const physY = (pyIdx - cy) * scaleYPerPixel;
                const sinT = physY / Math.sqrt(physY * physY + lM * lM);
                const beta = (Math.PI * aM * sinT) / wlM;
                const sinc = Math.abs(beta) > 1e-6 ? Math.sin(beta) / beta : 1.0;
                const alpha = (Math.PI * dM * sinT) / wlM;
                const intensity = (sinc * sinc) * Math.pow(Math.cos(alpha), 2);

                ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${Math.min(1.0, intensity)})`;
                ctx.fillRect(xScreen - 5, pyIdx, 10, 2);
            }

            // 5. Inspection Point P and Rays r1, r2
            const pyP = cy + waveTargetY;
            const pX = xScreen;

            ctx.strokeStyle = '#00E676';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 3]);
            ctx.beginPath();
            ctx.moveTo(s1.x, s1.y);
            ctx.lineTo(pX, pyP);
            ctx.stroke();

            ctx.strokeStyle = '#FFD600';
            ctx.beginPath();
            ctx.moveTo(s2.x, s2.y);
            ctx.lineTo(pX, pyP);
            ctx.stroke();
            ctx.setLineDash([]);

            // 6. Path Difference Right Triangle (Projection of S1 onto Ray S2-P)
            const vx = pX - s2.x;
            const vy = pyP - s2.y;
            const vLen = Math.hypot(vx, vy);
            if (vLen > 1e-3) {
                const ux = vx / vLen;
                const uy = vy / vLen;
                const wx = s1.x - s2.x;
                const wy = s1.y - s2.y;
                const proj = wx * ux + wy * uy;
                const hx = s2.x + proj * ux;
                const hy = s2.y + proj * uy;

                // Perpendicular from S1 to Ray S2-P
                ctx.strokeStyle = '#38BDF8';
                ctx.lineWidth = 1.2;
                ctx.setLineDash([3, 2]);
                ctx.beginPath();
                ctx.moveTo(s1.x, s1.y);
                ctx.lineTo(hx, hy);
                ctx.stroke();
                ctx.setLineDash([]);

                // Delta r segment on Ray S2
                ctx.strokeStyle = '#00F0FF';
                ctx.lineWidth = 3.5;
                ctx.beginPath();
                ctx.moveTo(s2.x, s2.y);
                ctx.lineTo(hx, hy);
                ctx.stroke();

                ctx.fillStyle = '#00F0FF';
                ctx.font = 'bold 11px Space Grotesk, sans-serif';
                ctx.fillText('Δr', (s2.x + hx) / 2 - 12, (s2.y + hy) / 2 + 14);
            }

            // Calculations at Point P
            const physYP = waveTargetY * scaleYPerPixel;
            const r1 = Math.hypot(lM, physYP - dM / 2);
            const r2 = Math.hypot(lM, physYP + dM / 2);
            const deltaR = Math.abs(r2 - r1);
            const deltaRNm = deltaR * 1e9;
            const phaseDeg = (360.0 * deltaR / wlM) % 360;
            const sinTP = physYP / Math.hypot(physYP, lM);
            const betaP = (Math.PI * aM * sinTP) / wlM;
            const sincP = Math.abs(betaP) > 1e-6 ? Math.sin(betaP) / betaP : 1.0;
            const alphaP = (Math.PI * dM * sinTP) / wlM;
            const intensityP = (sincP * sincP) * Math.pow(Math.cos(alphaP), 2);

            // Pulsating Luminous Spot at P
            const pulse = 0.75 + 0.25 * Math.sin(animPhase * 2);
            const spotR = Math.max(3, 11 * intensityP * pulse);

            if (intensityP > 0.25) {
                const grad = ctx.createRadialGradient(pX, pyP, 1, pX, pyP, spotR * 2);
                grad.addColorStop(0, '#FFFFFF');
                grad.addColorStop(0.4, color.hex);
                grad.addColorStop(1, 'transparent');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(pX, pyP, spotR * 2, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#FFFFFF';
                ctx.beginPath();
                ctx.arc(pX, pyP, 3, 0, Math.PI * 2);
                ctx.fill();
            } else {
                ctx.fillStyle = '#475569';
                ctx.beginPath();
                ctx.arc(pX, pyP, 3.5, 0, Math.PI * 2);
                ctx.fill();
            }

            // Point P label & drag handle
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 12px Space Grotesk, sans-serif';
            ctx.fillText(`P (${(intensityP * 100).toFixed(0)}%)`, pX + 14, pyP + 4);

            // 7. Telemetry HUD Bar at Top
            const orderM = deltaR / wlM;
            const nearM = Math.round(orderM);
            const fracM = orderM - Math.floor(orderM);
            let stateLabel = Math.abs(orderM - nearM) < 0.1 ? `[Max m=${nearM}]` : Math.abs(fracM - 0.5) < 0.1 ? '[Dark Min]' : '';
            ctx.fillStyle = '#38BDF8';
            ctx.font = 'bold 12px Space Grotesk, Vazirmatn, sans-serif';
            ctx.fillText(`Δr = ${deltaRNm.toFixed(1)} nm  |  Phase = ${phaseDeg.toFixed(0)}°  ${stateLabel}`, 30, 24);

            animPhase = (animPhase + 0.05) % (2 * Math.PI);
            animId = requestAnimationFrame(loop);
        }

        loop();
    }

    /**
     * 2. Interactive Path Difference Right-Triangle Visualizer for Slide 6 (c2_pathdiff)
     * Dedicated 60 FPS interactive canvas with draggable Point P, live right-triangle projection,
     * glowing Delta r segment (S2 - H), right-angle indicator, and real-time calculation telemetry.
     */
    function startTriangleAnimation(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let targetYP = 0;
        let isDraggingTriangleP = false;

        const wlNm = 632.8;
        const dMm = 0.25;
        const lM = 1.0;
        const color = wavelengthToHex(wlNm);

        function getCanvasCoords(e) {
            const rect = canvas.getBoundingClientRect();
            return {
                x: (e.clientX - rect.left) * (canvas.width / rect.width),
                y: (e.clientY - rect.top) * (canvas.height / rect.height)
            };
        }

        canvas.onpointerdown = (e) => {
            const pos = getCanvasCoords(e);
            const sx = canvas.width - 65;
            if (pos.x > sx - 90) {
                isDraggingTriangleP = true;
                targetYP = pos.y - canvas.height / 2;
                canvas.setPointerCapture(e.pointerId);
            }
        };

        canvas.onpointermove = (e) => {
            const pos = getCanvasCoords(e);
            const sx = canvas.width - 65;
            if (pos.x > sx - 90) {
                canvas.style.cursor = 'ns-resize';
            } else {
                canvas.style.cursor = 'default';
            }
            if (isDraggingTriangleP) {
                targetYP = Math.max(-canvas.height / 2 + 25, Math.min(canvas.height / 2 - 25, pos.y - canvas.height / 2));
            }
        };

        canvas.onpointerup = canvas.onpointercancel = (e) => {
            isDraggingTriangleP = false;
            try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
        };

        function loop() {
            const w = canvas.width = canvas.clientWidth || 800;
            const h = canvas.height = canvas.clientHeight || 380;
            const cy = h / 2;
            const xBarrier = Math.floor(w * 0.22);
            const xScreen = w - 105;
            const slitGap = 90;

            const s1 = { x: xBarrier, y: cy - slitGap / 2 };
            const s2 = { x: xBarrier, y: cy + slitGap / 2 };
            const pX = xScreen;
            const pY = cy + targetYP;

            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            // 1. Barrier Plate with Slits S1 & S2
            ctx.fillStyle = '#334155';
            ctx.strokeStyle = '#64748B';
            ctx.lineWidth = 2;
            ctx.fillRect(xBarrier - 6, 20, 12, s1.y - 20);
            ctx.fillRect(xBarrier - 6, s1.y + 6, 12, s2.y - s1.y - 12);
            ctx.fillRect(xBarrier - 6, s2.y + 6, 12, h - s2.y - 26);

            // Slit dots
            ctx.fillStyle = '#38BDF8';
            ctx.beginPath();
            ctx.arc(s1.x, s1.y, 5, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#F59E0B';
            ctx.beginPath();
            ctx.arc(s2.x, s2.y, 5, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#38BDF8';
            ctx.font = 'bold 12px Space Grotesk, sans-serif';
            ctx.fillText('S₁', s1.x - 24, s1.y + 4);
            ctx.fillStyle = '#F59E0B';
            ctx.fillText('S₂', s2.x - 24, s2.y + 4);

            // Slit separation d bracket
            ctx.strokeStyle = '#F59E0B';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(xBarrier - 16, s1.y);
            ctx.lineTo(xBarrier - 16, s2.y);
            ctx.stroke();
            ctx.fillText('d = 0.25mm', xBarrier - 65, cy + 4);

            // 2. Screen Plate
            ctx.fillStyle = '#0F172A';
            ctx.strokeStyle = '#38BDF8';
            ctx.lineWidth = 2;
            ctx.fillRect(xScreen - 6, 20, 12, h - 40);
            ctx.strokeRect(xScreen - 6, 20, 12, h - 40);

            // Horizontal reference line from midpoint of slits
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(xBarrier, cy);
            ctx.lineTo(xScreen, cy);
            ctx.stroke();
            ctx.setLineDash([]);

            // 3. Rays r1 and r2 to Point P
            ctx.strokeStyle = '#38BDF8';
            ctx.lineWidth = 2.5;
            ctx.setLineDash([6, 3]);
            ctx.beginPath();
            ctx.moveTo(s1.x, s1.y);
            ctx.lineTo(pX, pY);
            ctx.stroke();

            ctx.strokeStyle = '#F59E0B';
            ctx.beginPath();
            ctx.moveTo(s2.x, s2.y);
            ctx.lineTo(pX, pY);
            ctx.stroke();
            ctx.setLineDash([]);

            // Labels on rays
            ctx.fillStyle = '#38BDF8';
            ctx.font = 'bold 12px Space Grotesk, sans-serif';
            ctx.fillText('r₁', (s1.x + pX) / 2 - 20, (s1.y + pY) / 2 - 14);
            ctx.fillStyle = '#F59E0B';
            ctx.fillText('r₂', (s2.x + pX) / 2 - 20, (s2.y + pY) / 2 + 18);

            // 4. Geometric Path Difference Right Triangle (Projection of S1 onto Ray S2-P)
            const vx = pX - s2.x;
            const vy = pY - s2.y;
            const vLen = Math.hypot(vx, vy);
            if (vLen > 1e-3) {
                const ux = vx / vLen;
                const uy = vy / vLen;
                const wx = s1.x - s2.x;
                const wy = s1.y - s2.y;
                const proj = wx * ux + wy * uy;
                const hx = s2.x + proj * ux;
                const hy = s2.y + proj * uy;

                // Perpendicular dashed line from S1 to H
                ctx.strokeStyle = '#38BDF8';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([3, 2]);
                ctx.beginPath();
                ctx.moveTo(s1.x, s1.y);
                ctx.lineTo(hx, hy);
                ctx.stroke();
                ctx.setLineDash([]);

                // Right angle square indicator at H
                const normX = -uy * 10;
                const normY = ux * 10;
                ctx.strokeStyle = '#EF4444';
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo(hx - ux * 8, hy - uy * 8);
                ctx.lineTo(hx - ux * 8 + normX * 0.8, hy - uy * 8 + normY * 0.8);
                ctx.lineTo(hx + normX * 0.8, hy + normY * 0.8);
                ctx.stroke();

                // Point H
                ctx.fillStyle = '#EF4444';
                ctx.beginPath();
                ctx.arc(hx, hy, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillText('H', hx + 8, hy + 4);

                // Prominent glowing path difference segment S2 - H = Delta r
                const glowPulse = 0.8 + 0.2 * Math.sin(animPhase * 3);
                ctx.strokeStyle = '#00F0FF';
                ctx.lineWidth = 4 * glowPulse;
                ctx.beginPath();
                ctx.moveTo(s2.x, s2.y);
                ctx.lineTo(hx, hy);
                ctx.stroke();

                // Delta r callout badge
                const midHx = (s2.x + hx) / 2;
                const midHy = (s2.y + hy) / 2;
                ctx.fillStyle = '#060911';
                ctx.strokeStyle = '#00F0FF';
                ctx.lineWidth = 1.5;
                ctx.fillRect(midHx - 55, midHy - 12, 110, 24);
                ctx.strokeRect(midHx - 55, midHy - 12, 110, 24);
                ctx.fillStyle = '#00F0FF';
                ctx.font = 'bold 12px Space Grotesk, sans-serif';
                ctx.fillText('Δr = d·sinθ', midHx - 40, midHy + 4);
            }

            // Calculations
            const scaleY = 0.0003;
            const physY = targetYP * scaleY;
            const r1Len = Math.hypot(lM, physY - (dMm * 1e-3) / 2);
            const r2Len = Math.hypot(lM, physY + (dMm * 1e-3) / 2);
            const deltaR = Math.abs(r2Len - r1Len);
            const deltaRNm = deltaR * 1e9;
            const thetaRad = Math.atan2(physY, lM);
            const thetaDeg = thetaRad * (180 / Math.PI);
            const phaseDeg = (360.0 * deltaR / (wlNm * 1e-9)) % 360;
            const orderM = deltaR / (wlNm * 1e-9);
            const nearM = Math.round(orderM);
            const fracM = orderM - Math.floor(orderM);

            const isMax = Math.abs(orderM - nearM) < 0.08;
            const isMin = Math.abs(fracM - 0.5) < 0.08;
            let statusText = isMax ? `✓ بیشینه روشن (مرتبه m=${nearM})` : isMin ? '✗ گره تاریک (کمینه)' : 'ناحیه میانی';

            // Point P pulsating spot
            const pulse = 0.75 + 0.25 * Math.sin(animPhase * 2);
            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.arc(pX, pY, 7 * pulse, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = isMax ? '#10B981' : isMin ? '#EF4444' : '#00E676';
            ctx.lineWidth = 2.5;
            ctx.stroke();

            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 12px Space Grotesk, sans-serif';
            ctx.fillText(`P (y = ${(targetYP).toFixed(0)}px)`, pX + 16, pY + 4);

            // Telemetry HUD Banner at top
            ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
            ctx.fillRect(20, 10, w - 40, 32);
            ctx.strokeStyle = '#1E293B';
            ctx.strokeRect(20, 10, w - 40, 32);

            ctx.fillStyle = '#00F0FF';
            ctx.font = 'bold 12px Space Grotesk, Vazirmatn, sans-serif';
            ctx.fillText(`اختلاف راه: Δr = ${deltaRNm.toFixed(1)} nm  |  زاویه: θ = ${thetaDeg.toFixed(2)}°  |  اختلاف فاز: Δφ = ${phaseDeg.toFixed(0)}°  |  ${statusText}`, 30, 31);

            animPhase = (animPhase + 0.04) % (2 * Math.PI);
            animId = requestAnimationFrame(loop);
        }

        loop();
    }

    /**
     * 3. Historical Duel Visualizer: Newton Particles vs. Huygens Waves
     */
    function startDuelAnimation(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let pellets = [];

        function loop() {
            const w = canvas.width = canvas.clientWidth || 800;
            const h = canvas.height = canvas.clientHeight || 380;
            const midX = w / 2;
            const cy = h / 2;

            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            // Divider line
            ctx.strokeStyle = '#1E293B';
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 4]);
            ctx.beginPath();
            ctx.moveTo(midX, 10);
            ctx.lineTo(midX, h - 10);
            ctx.stroke();
            ctx.setLineDash([]);

            // ================= LEFT: NEWTON'S PARTICLES =================
            ctx.fillStyle = '#93C5FD';
            ctx.font = 'bold 12px Vazirmatn, Space Grotesk, sans-serif';
            ctx.fillText('نیوتن (۱۷۰۴): ذرات بالستیک (V = 0)', 30, 25);

            // Barrier & Screen
            const bLeft = midX * 0.55;
            const sLeft = midX - 25;
            ctx.fillStyle = '#334155';
            ctx.fillRect(bLeft, 20, 8, cy - 35);
            ctx.fillRect(bLeft, cy - 15, 8, 30);
            ctx.fillRect(bLeft, cy + 35, 8, h - cy - 55);

            ctx.fillStyle = '#0F172A';
            ctx.strokeStyle = '#EF4444';
            ctx.strokeRect(sLeft, 20, 8, h - 40);

            // Emit pellets
            if (Math.random() < 0.4) {
                const slitY = Math.random() < 0.5 ? cy - 25 : cy + 25;
                pellets.push({ x: 20, y: slitY, targetY: slitY + (Math.random() - 0.5) * 8 });
            }

            // Update & draw pellets
            for (let i = pellets.length - 1; i >= 0; i--) {
                const p = pellets[i];
                p.x += 6;
                ctx.fillStyle = '#EF4444';
                ctx.beginPath();
                ctx.arc(p.x, p.targetY, 2.5, 0, Math.PI * 2);
                ctx.fill();

                if (p.x >= sLeft) {
                    pellets.splice(i, 1);
                }
            }

            // Two distinct particle stripes on screen
            ctx.fillStyle = 'rgba(239, 68, 68, 0.7)';
            ctx.fillRect(sLeft + 1, cy - 35, 6, 20);
            ctx.fillRect(sLeft + 1, cy + 15, 6, 20);

            // ================= RIGHT: HUYGENS WAVES =================
            ctx.fillStyle = '#6EE7B7';
            ctx.fillText('هویگنس (۱۶۹۰): موجک‌های هم‌پوشان (V = 1)', midX + 30, 25);

            const bRight = midX + (w - midX) * 0.45;
            const sRight = w - 25;

            ctx.fillStyle = '#334155';
            ctx.fillRect(bRight, 20, 8, cy - 35);
            ctx.fillRect(bRight, cy - 15, 8, 30);
            ctx.fillRect(bRight, cy + 35, 8, h - cy - 55);

            ctx.fillStyle = '#0F172A';
            ctx.strokeStyle = '#10B981';
            ctx.strokeRect(sRight, 20, 8, h - 40);

            // Expanding wavelets
            for (let r = 10; r < 140; r += 20) {
                const rr = r + 4 * Math.sin(animPhase);
                ctx.strokeStyle = 'rgba(16, 185, 129, 0.45)';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.arc(bRight + 4, cy - 25, rr, -Math.PI * 0.4, Math.PI * 0.4);
                ctx.stroke();

                ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
                ctx.beginPath();
                ctx.arc(bRight + 4, cy + 25, rr, -Math.PI * 0.4, Math.PI * 0.4);
                ctx.stroke();
            }

            // Alternating fringes on screen
            for (let y = cy - 70; y <= cy + 70; y += 14) {
                ctx.fillStyle = 'rgba(16, 185, 129, 0.85)';
                ctx.fillRect(sRight + 1, y, 6, 6);
            }

            animPhase = (animPhase + 0.08) % (2 * Math.PI);
            animId = requestAnimationFrame(loop);
        }

        loop();
    }

    /**
     * 4. Wave Superposition & Phasor Circle Visualizer
     */
    function startInterferenceAnimation(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        function loop() {
            const w = canvas.width = canvas.clientWidth || 800;
            const h = canvas.height = canvas.clientHeight || 380;
            const cy = h / 2;

            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            // Left Plot: Superposed waves
            const plotW = Math.floor(w * 0.62);
            ctx.fillStyle = '#111827';
            ctx.strokeStyle = '#374151';
            ctx.lineWidth = 1;
            ctx.fillRect(20, 30, plotW, h - 60);
            ctx.strokeRect(20, 30, plotW, h - 60);

            ctx.strokeStyle = '#475569';
            ctx.beginPath();
            ctx.moveTo(20, cy);
            ctx.lineTo(20 + plotW, cy);
            ctx.stroke();

            // Wave curves
            ctx.lineWidth = 1.5;
            const phase = animPhase;

            // E1 (Cyan)
            ctx.strokeStyle = '#38BDF8';
            ctx.setLineDash([4, 2]);
            ctx.beginPath();
            for (let x = 0; x < plotW; x++) {
                const y = cy - 25 * Math.sin(x * 0.06 - phase);
                if (x === 0) ctx.moveTo(20 + x, y);
                else ctx.lineTo(20 + x, y);
            }
            ctx.stroke();

            // E2 (Amber)
            ctx.strokeStyle = '#F59E0B';
            ctx.beginPath();
            for (let x = 0; x < plotW; x++) {
                const y = cy - 25 * Math.sin(x * 0.06 - phase);
                if (x === 0) ctx.moveTo(20 + x, y);
                else ctx.lineTo(20 + x, y);
            }
            ctx.stroke();
            ctx.setLineDash([]);

            // Resultant E_net = E1 + E2 (Emerald)
            ctx.strokeStyle = '#10B981';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            for (let x = 0; x < plotW; x++) {
                const y = cy - 50 * Math.sin(x * 0.06 - phase);
                if (x === 0) ctx.moveTo(20 + x, y);
                else ctx.lineTo(20 + x, y);
            }
            ctx.stroke();

            ctx.fillStyle = '#10B981';
            ctx.font = 'bold 12px Vazirmatn, sans-serif';
            ctx.fillText('E_net = E₁ + E₂ (تداخل سازنده بیشینه: I = 4I₀)', 35, 52);

            // Right Plot: Phasor Circle
            const phasorX = Math.floor(w * 0.82);
            const rCirc = 55;

            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(phasorX, cy, rCirc, 0, Math.PI * 2);
            ctx.stroke();

            ctx.strokeStyle = '#374151';
            ctx.beginPath();
            ctx.moveTo(phasorX - rCirc - 10, cy);
            ctx.lineTo(phasorX + rCirc + 10, cy);
            ctx.moveTo(phasorX, cy - rCirc - 10);
            ctx.lineTo(phasorX, cy + rCirc + 10);
            ctx.stroke();

            // Rotating Phasor Vector
            const px = phasorX + rCirc * Math.cos(phase);
            const py = cy - rCirc * Math.sin(phase);

            ctx.strokeStyle = '#38BDF8';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(phasorX, cy);
            ctx.lineTo(px, py);
            ctx.stroke();

            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 11px Space Grotesk, sans-serif';
            ctx.fillText('E_net', px + 6, py);

            animPhase = (animPhase + 0.04) % (2 * Math.PI);
            animId = requestAnimationFrame(loop);
        }

        loop();
    }

    /**
     * 5. Analytical Fringe & Caliper Ruler Visualizer
     */
    function startAnalyticalFringe(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width = canvas.clientWidth || 800;
        const h = canvas.height = canvas.clientHeight || 380;
        const cy = h / 2;

        ctx.fillStyle = '#060911';
        ctx.fillRect(0, 0, w, h);

        // Top: Interference Ribbon
        ctx.fillStyle = '#0F172A';
        ctx.fillRect(40, 30, w - 80, 50);

        for (let x = 40; x < w - 40; x++) {
            const dx = (x - w / 2) / 22.0;
            const inten = Math.pow(Math.cos(dx * 1.5), 2) * Math.exp(-(dx * dx) / 18.0);
            ctx.fillStyle = `rgba(239, 68, 68, ${Math.min(1.0, inten * 1.2)})`;
            ctx.fillRect(x, 30, 1, 50);
        }

        // Caliper Ruler
        const dyPixels = 46;
        const m0X = w / 2;
        const m1X = m0X + dyPixels;

        ctx.strokeStyle = '#F59E0B';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(m0X, 85);
        ctx.lineTo(m0X, 105);
        ctx.moveTo(m1X, 85);
        ctx.lineTo(m1X, 105);
        ctx.moveTo(m0X, 95);
        ctx.lineTo(m1X, 95);
        ctx.stroke();

        ctx.fillStyle = '#F59E0B';
        ctx.font = 'bold 13px Space Grotesk, Vazirmatn, sans-serif';
        ctx.fillText('فاصله دو نوار: Δy = λL / d = 2.53 mm', m0X - 70, 125);

        // Intensity curve
        ctx.strokeStyle = '#EF4444';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        for (let x = 40; x < w - 40; x++) {
            const dx = (x - w / 2) / 22.0;
            const inten = Math.pow(Math.cos(dx * 1.5), 2) * Math.exp(-(dx * dx) / 18.0);
            const yPlot = cy + 120 - inten * 80;
            if (x === 40) ctx.moveTo(x, yPlot);
            else ctx.lineTo(x, yPlot);
        }
        ctx.stroke();

        ctx.fillStyle = '#94A3B8';
        ctx.font = 'bold 11px Space Grotesk, sans-serif';
        ctx.fillText('m = -2', m0X - 2 * dyPixels - 14, cy + 140);
        ctx.fillText('m = -1', m0X - dyPixels - 14, cy + 140);
        ctx.fillText('m = 0 (مرکزی)', m0X - 24, cy + 140);
        ctx.fillText('m = +1', m0X + dyPixels - 14, cy + 140);
        ctx.fillText('m = +2', m0X + 2 * dyPixels - 14, cy + 140);
    }

    /**
     * 6. Worked Example Bench with Screen Magnifier
     */
    function startWorkedBenchVisualizer(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width = canvas.clientWidth || 800;
        const h = canvas.height = canvas.clientHeight || 380;
        const cy = h / 2;

        ctx.fillStyle = '#060911';
        ctx.fillRect(0, 0, w, h);

        // Optical bench track
        ctx.fillStyle = '#1E293B';
        ctx.fillRect(40, cy + 40, w - 80, 16);

        // Laser source
        ctx.fillStyle = '#334155';
        ctx.strokeStyle = '#EF4444';
        ctx.lineWidth = 2;
        ctx.fillRect(60, cy - 20, 60, 45);
        ctx.strokeRect(60, cy - 20, 60, 45);
        ctx.fillStyle = '#EF4444';
        ctx.font = 'bold 10px Space Grotesk';
        ctx.fillText('He-Ne 632.8nm', 64, cy + 8);

        // Slits
        const slitX = Math.max(180, Math.floor(w * 0.30));
        ctx.fillStyle = '#475569';
        ctx.fillRect(slitX, cy - 35, 10, 75);
        ctx.fillStyle = '#F59E0B';
        ctx.fillText('d = 0.25mm', slitX - 20, cy - 42);

        // Screen
        const scrX = Math.max(slitX + 120, Math.floor(w * 0.56));
        ctx.fillStyle = '#0F172A';
        ctx.strokeStyle = '#38BDF8';
        ctx.fillRect(scrX, cy - 50, 12, 105);
        ctx.strokeRect(scrX, cy - 50, 12, 105);
        ctx.fillStyle = '#38BDF8';
        ctx.fillText('L = 1.0 m', scrX - 15, cy + 72);

        // Laser beam
        ctx.strokeStyle = '#EF4444';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(120, cy + 2);
        ctx.lineTo(slitX, cy + 2);
        ctx.stroke();

        ctx.setLineDash([4, 2]);
        ctx.beginPath();
        ctx.moveTo(slitX + 10, cy + 2);
        ctx.lineTo(scrX, cy - 20);
        ctx.moveTo(slitX + 10, cy + 2);
        ctx.lineTo(scrX, cy + 25);
        ctx.stroke();
        ctx.setLineDash([]);

        // Magnifying Loupe on right
        const loupeX = Math.max(scrX + 100, Math.floor(w * 0.82));
        const loupeR = 75;

        ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
        ctx.strokeStyle = '#00F0FF';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(loupeX, cy, loupeR, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Magnified fringes inside loupe
        for (let x = loupeX - loupeR + 10; x < loupeX + loupeR - 10; x++) {
            const dx = (x - loupeX) / 18.0;
            const inten = Math.pow(Math.cos(dx * 1.5), 2);
            ctx.fillStyle = `rgba(239, 68, 68, ${inten})`;
            ctx.fillRect(x, cy - 45, 1, 90);
        }

        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 12px Vazirmatn, Space Grotesk, sans-serif';
        ctx.fillText('بزرگ‌نمایی پرده: Δy = ۲٫۵۳ mm', loupeX - 65, cy + loupeR + 24);
    }

    /**
     * 7. Single-Slit Sinc² Envelope & Missing Orders
     */
    function startEnvelopeAnimation(canvas) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width = canvas.clientWidth || 800;
        const h = canvas.height = canvas.clientHeight || 380;
        const cy = h / 2;

        ctx.fillStyle = '#060911';
        ctx.fillRect(0, 0, w, h);

        const xCenter = w / 2;
        const scaleX = 26;

        // Baseline
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(30, cy + 80);
        ctx.lineTo(w - 30, cy + 80);
        ctx.stroke();

        // 1. Sinc^2 Envelope (Dashed Amber)
        ctx.strokeStyle = '#F59E0B';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 3]);
        ctx.beginPath();
        for (let x = 30; x < w - 30; x++) {
            const theta = (x - xCenter) / (scaleX * 4);
            const beta = Math.PI * theta;
            const sinc = Math.abs(beta) > 1e-4 ? Math.sin(beta) / beta : 1.0;
            const env = sinc * sinc;
            const y = cy + 80 - env * 140;
            if (x === 30) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // 2. Modulated Interference Fringes (Cyan)
        ctx.strokeStyle = '#00F0FF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let x = 30; x < w - 30; x++) {
            const theta = (x - xCenter) / scaleX;
            const beta = Math.PI * (theta / 4);
            const sinc = Math.abs(beta) > 1e-4 ? Math.sin(beta) / beta : 1.0;
            const cosVal = Math.cos(Math.PI * theta);
            const total = (sinc * sinc) * (cosVal * cosVal);
            const y = cy + 80 - total * 140;
            if (x === 30) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();

        // 3. Highlight Missing Orders at m = +/-4
        const missX1 = xCenter - 4 * scaleX;
        const missX2 = xCenter + 4 * scaleX;

        ctx.strokeStyle = '#EF4444';
        ctx.lineWidth = 2;
        ctx.setLineDash([3, 2]);
        ctx.beginPath();
        ctx.moveTo(missX1, cy - 70);
        ctx.lineTo(missX1, cy + 80);
        ctx.moveTo(missX2, cy - 70);
        ctx.lineTo(missX2, cy + 80);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = '#EF4444';
        ctx.font = 'bold 11px Vazirmatn, sans-serif';
        ctx.fillText('مرتبه غایب m = -۴', missX1 - 42, cy - 80);
        ctx.fillText('مرتبه غایب m = +۴', missX2 - 42, cy - 80);

        ctx.fillStyle = '#F59E0B';
        ctx.fillText('پوش پراش تک‌شکاف: sinc²(β)', 40, 40);
        ctx.fillStyle = '#00F0FF';
        ctx.fillText('شدت کل تداخل دوشکاف', 40, 60);
    }

    /**
     * 8. Quantum Particle Buildup Simulation with Toggleable Which-Way Observer
     */
    function startQuantumBuildup(canvas, isObserverActive) {
        stopAllAnimations();
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        buildupParticles = [];
        buildupObserver = Boolean(isObserverActive);

        function emitBurst() {
            const w = canvas.width = canvas.clientWidth || 800;
            const h = canvas.height = canvas.clientHeight || 380;

            for (let i = 0; i < 16; i++) {
                const xFrac = Math.random();
                let prob;
                if (!buildupObserver) {
                    // Coherent superposition: cos^2 pattern
                    prob = Math.pow(Math.cos((xFrac - 0.5) * Math.PI * 7.5), 2) * Math.exp(-Math.pow(xFrac - 0.5, 2) / 0.08);
                } else {
                    // Incoherent clumps: two classical peaks
                    prob = 0.5 * (Math.exp(-Math.pow(xFrac - 0.42, 2) / 0.012) + Math.exp(-Math.pow(xFrac - 0.58, 2) / 0.012));
                }

                if (Math.random() < prob) {
                    const px = Math.floor(xFrac * (w - 80) + 40);
                    const py = Math.floor(h / 2 + (Math.random() - 0.5) * 85);
                    buildupParticles.push({ x: px, y: py, age: 0 });
                    if (buildupParticles.length > 1400) {
                        buildupParticles.shift();
                    }
                }
            }

            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            for (const p of buildupParticles) {
                if (p.age < 3) {
                    ctx.fillStyle = '#FFFFFF';
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                    ctx.fill();
                    p.age++;
                } else {
                    ctx.fillStyle = buildupObserver ? '#F59E0B' : '#00E676';
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            ctx.fillStyle = '#94A3B8';
            ctx.font = 'bold 13px Space Grotesk, sans-serif';
            ctx.fillText(`N = ${buildupParticles.length} hits  |  V = ${buildupObserver ? '0.00' : '0.98'}`, w - 210, 28);

            ctx.fillStyle = buildupObserver ? '#EF4444' : '#10B981';
            ctx.font = 'bold 13px Vazirmatn, sans-serif';
            ctx.fillText(buildupObserver ? 'ناظر فعال: فروپاشی موج → دو لکه ذره‌ای' : 'برهم‌نهی کوانتومی همدوس (|ψ₁ + ψ₂|²)', 25, 28);
        }

        buildupTimer = setInterval(emitBurst, 50);
    }

    function toggleQuantumObserver() {
        buildupObserver = !buildupObserver;
        buildupParticles = [];
        return buildupObserver;
    }

    function setQuantumObserver(active) {
        buildupObserver = Boolean(active);
        buildupParticles = [];
        return buildupObserver;
    }

    /**
     * 9. Fallback Scalable Vector Graphic (SVG) Ray Tracing Generator
     */
    function renderRayTracingSVG(targetYPercent = 50) {
        const py = 50 + (targetYPercent / 100) * 260;
        return `
        <svg viewBox="0 0 800 360" width="100%" height="340" style="background:#060911; border-radius:12px;">
            <rect x="30" y="150" width="70" height="50" rx="6" fill="#1E293B" stroke="#3B82F6" stroke-width="2"/>
            <text x="65" y="180" fill="#93C5FD" font-size="11" font-weight="bold" text-anchor="middle" font-family="Space Grotesk">LASER</text>
            <line x1="100" y1="175" x2="310" y2="175" stroke="#EF4444" stroke-width="4"/>
            <rect x="310" y="20" width="12" height="110" fill="#475569"/>
            <rect x="310" y="160" width="12" height="30" fill="#475569"/>
            <rect x="310" y="220" width="12" height="110" fill="#475569"/>
            <circle cx="316" cy="145" r="4" fill="#38BDF8"/>
            <circle cx="316" cy="205" r="4" fill="#F59E0B"/>
            <text x="295" y="150" fill="#38BDF8" font-weight="bold" font-size="12">S₁</text>
            <text x="295" y="210" fill="#F59E0B" font-weight="bold" font-size="12">S₂</text>
            <rect x="710" y="20" width="12" height="320" rx="3" fill="#0F172A" stroke="#3B82F6" stroke-width="2"/>
            <line x1="316" y1="145" x2="710" y2="${py}" stroke="#38BDF8" stroke-width="2.5" stroke-dasharray="6,3"/>
            <line x1="316" y1="205" x2="710" y2="${py}" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="6,3"/>
            <line x1="316" y1="145" x2="335" y2="198" stroke="#EF4444" stroke-width="3"/>
            <text x="345" y="180" fill="#EF4444" font-weight="bold" font-size="12">Δr = d·sinθ</text>
            <circle cx="710" cy="${py}" r="7" fill="#FFFFFF" stroke="#10B981" stroke-width="3"/>
            <text x="735" y="${py + 4}" fill="#FFFFFF" font-weight="bold" font-size="13">P</text>
        </svg>`;
    }

    function stopAllAnimations() {
        if (animId) {
            cancelAnimationFrame(animId);
            animId = null;
        }
        if (buildupTimer) {
            clearInterval(buildupTimer);
            buildupTimer = null;
        }
    }

    return {
        wavelengthToHex,
        startHuygensAnimation,
        startTriangleAnimation,
        startDuelAnimation,
        startInterferenceAnimation,
        startAnalyticalFringe,
        startWorkedBenchVisualizer,
        startEnvelopeAnimation,
        startQuantumBuildup,
        toggleQuantumObserver,
        setQuantumObserver,
        renderRayTracingSVG,
        stopAllAnimations
    };
})();
